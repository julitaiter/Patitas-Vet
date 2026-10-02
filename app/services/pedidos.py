import logging
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

from app.models import (ComprobanteTransferencia, ConfiguracionCheckout, CuentaTransferencia,
                        HistorialEstadoPedido, Pedido, PedidoItem, Producto)


logger = logging.getLogger(__name__)


class PedidoError(ValueError):
    pass


def generar_codigo_pedido():
    for _ in range(20):
        codigo = timezone.localdate().strftime("%Y%m%d") + f"{secrets.randbelow(1000000):06d}"
        if not Pedido.objects.filter(codigo=codigo).exists():
            return codigo
    raise PedidoError("No se pudo generar un código de pedido. Intentá nuevamente.")


def obtener_configuracion_checkout():
    configuracion, _ = ConfiguracionCheckout.objects.get_or_create(pk=1)
    return configuracion


def obtener_cuenta_transferencia():
    return CuentaTransferencia.objects.filter(activa=True, principal=True).first()


def calcular_costo_envio(subtotal, tipo_entrega, configuracion):
    if tipo_entrega == "retiro":
        return Decimal("0.00")
    if configuracion.envio_gratis_desde is not None and subtotal >= configuracion.envio_gratis_desde:
        return Decimal("0.00")
    return configuracion.costo_envio


def calcular_totales(lineas, tipo_entrega, configuracion):
    subtotal = sum((producto.precio * cantidad for producto, cantidad in lineas), Decimal("0.00"))
    envio = calcular_costo_envio(subtotal, tipo_entrega, configuracion)
    return subtotal, envio, subtotal + envio


def validar_carrito(payload):
    if not isinstance(payload, list) or not payload:
        raise PedidoError("El carrito está vacío.")
    cantidades = {}
    for item in payload:
        if not isinstance(item, dict) or isinstance(item.get("id"), bool) or isinstance(item.get("cantidad"), bool):
            raise PedidoError("El carrito contiene datos inválidos.")
        try:
            pk, cantidad = int(item["id"]), int(item["cantidad"])
        except (KeyError, TypeError, ValueError):
            raise PedidoError("El carrito contiene datos inválidos.") from None
        if pk <= 0 or cantidad <= 0 or str(item["cantidad"]) != str(cantidad):
            raise PedidoError("Las cantidades deben ser enteros positivos.")
        if pk in cantidades:
            raise PedidoError("Hay productos duplicados en el carrito.")
        cantidades[pk] = cantidad
    return cantidades


@transaction.atomic
def crear_pedido(*, usuario, datos, carrito, configuracion):
    cantidades = validar_carrito(carrito)
    productos = list(Producto.objects.select_for_update().filter(pk__in=cantidades).order_by("pk"))
    if len(productos) != len(cantidades):
        raise PedidoError("Uno de los productos ya no existe.")
    lineas = []
    for producto in productos:
        cantidad = cantidades[producto.pk]
        if not producto.activo or producto.stock < cantidad:
            raise PedidoError(f"No hay stock suficiente de {producto.nombre}.")
        lineas.append((producto, cantidad))
    subtotal, envio, total = calcular_totales(lineas, datos["tipo_entrega"], configuracion)
    campos = {campo.name for campo in Pedido._meta.fields} - {"id", "usuario", "codigo", "estado", "estado_pago", "subtotal", "costo_envio", "total", "stock_reintegrado", "confirmed_at", "cancelled_at", "created_at", "updated_at"}
    valores = {clave: datos[clave] for clave in campos if clave in datos}
    transferencia = datos["medio_pago"] == "transferencia"
    pedido = Pedido.objects.create(
        usuario=usuario, codigo=generar_codigo_pedido(),
        estado="pago_informado" if transferencia else "nuevo",
        estado_pago="informado" if transferencia else "pendiente",
        subtotal=subtotal, costo_envio=envio, total=total,
        confirmed_at=timezone.now(), **valores,
    )
    for producto, cantidad in lineas:
        # El UPDATE condicional protege también en SQLite, donde select_for_update no bloquea filas.
        if not Producto.objects.filter(pk=producto.pk, activo=True, stock__gte=cantidad).update(stock=F("stock") - cantidad):
            raise PedidoError(f"No hay stock suficiente de {producto.nombre}.")
        PedidoItem.objects.create(pedido=pedido, producto=producto, producto_nombre=producto.nombre,
                                  precio_unitario=producto.precio, cantidad=cantidad, subtotal=producto.precio * cantidad)
    if transferencia:
        archivo = datos["comprobante"]
        ComprobanteTransferencia.objects.create(
            pedido=pedido, archivo=archivo, nombre_original=archivo.name,
            content_type=getattr(archivo, "content_type", "application/octet-stream"), tamanio=archivo.size,
        )
    HistorialEstadoPedido.objects.create(pedido=pedido, estado_nuevo=pedido.estado, usuario=usuario, observacion="Pedido creado")
    HistorialEstadoPedido.objects.create(pedido=pedido, estado_anterior=pedido.estado, estado_nuevo=pedido.estado,
                                        usuario=usuario, observacion="Checkout confirmado por el comprador")
    transaction.on_commit(lambda: enviar_emails_pedido(pedido.pk))
    return pedido


@transaction.atomic
def reintegrar_stock_pedido(pedido):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.stock_reintegrado:
        return False
    for item in pedido.items.select_related("producto").order_by("producto_id"):
        Producto.objects.filter(pk=item.producto_id).update(stock=F("stock") + item.cantidad)
    pedido.stock_reintegrado = True
    pedido.save(update_fields=["stock_reintegrado", "updated_at"])
    return True


@transaction.atomic
def cancelar_pedido(pedido, usuario=None, observacion=""):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.estado == "cancelado":
        return pedido
    if pedido.estado == "entregado":
        raise PedidoError("No se puede cancelar un pedido entregado.")
    anterior = pedido.estado
    reintegrar_stock_pedido(pedido)
    pedido.estado = "cancelado"
    pedido.cancelled_at = timezone.now()
    pedido.save(update_fields=["estado", "cancelled_at", "updated_at"])
    HistorialEstadoPedido.objects.create(pedido=pedido, estado_anterior=anterior, estado_nuevo="cancelado", usuario=usuario, observacion=observacion)
    return pedido


@transaction.atomic
def cambiar_estado_pedido(pedido, estado, usuario=None, observacion=""):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if estado not in dict(Pedido.ESTADOS):
        raise PedidoError("Estado de pedido inválido.")
    if estado == "cancelado":
        return cancelar_pedido(pedido, usuario, observacion)
    if pedido.estado == "cancelado":
        raise PedidoError("No se puede reabrir un pedido cancelado.")
    if estado != pedido.estado:
        anterior = pedido.estado
        pedido.estado = estado
        pedido.save(update_fields=["estado", "updated_at"])
        HistorialEstadoPedido.objects.create(pedido=pedido, estado_anterior=anterior, estado_nuevo=estado, usuario=usuario, observacion=observacion)
    return pedido


def enviar_emails_pedido(pedido_pk):
    pedido = Pedido.objects.prefetch_related("items").get(pk=pedido_pk)
    configuracion = obtener_configuracion_checkout()
    contexto = {"pedido": pedido}
    destinos = [(pedido.comprador_email, "cliente")]
    if configuracion.email_negocio:
        destinos.append((configuracion.email_negocio, "negocio"))
    for destino, tipo in destinos:
        try:
            mensaje = EmailMultiAlternatives(
                f"Pedido {pedido.codigo} | Patitas Vet",
                render_to_string(f"emails/pedido_{tipo}.txt", contexto),
                settings.DEFAULT_FROM_EMAIL, [destino],
            )
            mensaje.attach_alternative(render_to_string(f"emails/pedido_{tipo}.html", contexto), "text/html")
            mensaje.send()
        except Exception:
            logger.exception("No se pudo enviar email de pedido %s a %s", pedido.codigo, destino)
