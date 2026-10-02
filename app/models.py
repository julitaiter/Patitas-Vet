from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from ckeditor_uploader.fields import RichTextUploadingField
from simple_history.models import HistoricalRecords


def catalogo_imagen_upload_to(instance, filename):
    return f"{instance._meta.verbose_name_plural}/{filename}"


class BasicModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Categoria(BasicModel):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Sala(BasicModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "sala"
        verbose_name_plural = "salas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ItemCatalogo(BasicModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(
        upload_to=catalogo_imagen_upload_to, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Servicio(ItemCatalogo):
    duracion_minutos = models.PositiveIntegerField(default=30)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"


class Producto(ItemCatalogo):
    stock = models.PositiveIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"


class PreguntaFrecuente(BasicModel):
    pregunta = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()
    contenido = RichTextUploadingField(config_name="default")
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "pregunta frecuente"
        verbose_name_plural = "preguntas frecuentes"
        ordering = ["orden", "pregunta"]

    def __str__(self):
        return self.pregunta


class DisponibilidadTurno(BasicModel):
    DIA_LUNES = 0
    DIA_MARTES = 1
    DIA_MIERCOLES = 2
    DIA_JUEVES = 3
    DIA_VIERNES = 4
    DIA_SABADO = 5
    DIA_DOMINGO = 6

    DIAS_SEMANA = [
        (DIA_LUNES, "Lunes"),
        (DIA_MARTES, "Martes"),
        (DIA_MIERCOLES, "Miércoles"),
        (DIA_JUEVES, "Jueves"),
        (DIA_VIERNES, "Viernes"),
        (DIA_SABADO, "Sábado"),
        (DIA_DOMINGO, "Domingo"),
    ]

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    intervalo_minutos = models.PositiveIntegerField(default=30)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "disponibilidad de turno"
        verbose_name_plural = "disponibilidades de turnos"
        ordering = ["servicio", "sala", "dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["servicio", "sala", "dia_semana", "hora_inicio", "hora_fin"],
                name="disponibilidad_unica_por_servicio_sala_dia_horario",
            )
        ]

    def __str__(self):
        return f"{self.servicio} - {self.sala} - {self.get_dia_semana_display()} {self.hora_inicio} a {self.hora_fin}"


class Turno(BasicModel):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADO = "confirmado"
    ESTADO_CANCELADO = "cancelado"
    ESTADO_REALIZADO = "realizado"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_CONFIRMADO, "Confirmado"),
        (ESTADO_CANCELADO, "Cancelado"),
        (ESTADO_REALIZADO, "Realizado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name="turnos", blank=True, null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    mascota = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
    )

    class Meta:
        verbose_name = "turno"
        verbose_name_plural = "turnos"
        ordering = ["fecha", "hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["sala", "fecha", "hora"],
                name="turno_unico_por_sala_fecha_hora",
                condition=~models.Q(estado="cancelado"),
            )
        ]

    def __str__(self):
        return f"{self.servicio} - {self.fecha} {self.hora}"


class ConfiguracionCheckout(BasicModel):
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=4000, validators=[MinValueValidator(Decimal("0"))])
    envio_gratis_desde = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    nombre_tienda = models.CharField(max_length=150, blank=True)
    direccion_tienda = models.CharField(max_length=255, blank=True)
    indicaciones_retiro = models.TextField(blank=True)
    email_negocio = models.EmailField(blank=True)
    comprobante_max_mb = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1)])

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuración de checkout"


class CuentaTransferencia(BasicModel):
    banco = models.CharField(max_length=120)
    titular = models.CharField(max_length=150)
    cuit = models.CharField(max_length=20)
    alias = models.CharField(max_length=100)
    cbu_cvu = models.CharField(max_length=30)
    tipo_cuenta = models.CharField(max_length=80)
    moneda = models.CharField(max_length=20, default="ARS")
    observaciones = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    principal = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["principal"], condition=models.Q(principal=True, activa=True), name="una_cuenta_principal_activa")]

    def __str__(self):
        return f"{self.banco} - {self.alias}"


class Pedido(BasicModel):
    ESTADOS = [(x, x.replace("_", " ").capitalize()) for x in ("nuevo", "pendiente_pago", "pago_informado", "confirmado", "preparando", "listo", "entregado", "cancelado")]
    ESTADOS_PAGO = [(x, x.capitalize()) for x in ("pendiente", "informado", "acreditado", "rechazado")]
    FACTURAS = [("B", "Factura B"), ("A", "Factura A"), ("E", "Factura E")]
    ENTREGAS = [("retiro", "Retiro en tienda"), ("envio", "Envío a domicilio")]
    PAGOS = [("efectivo", "Efectivo"), ("transferencia", "Transferencia")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos")
    codigo = models.CharField(max_length=14, unique=True, editable=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="nuevo")
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default="pendiente")
    comprador_nombre = models.CharField(max_length=100)
    comprador_apellido = models.CharField(max_length=100)
    comprador_email = models.EmailField()
    comprador_telefono = models.CharField(max_length=40)
    comprador_dni = models.CharField(max_length=20)
    tipo_factura = models.CharField(max_length=1, choices=FACTURAS, default="B")
    facturacion_mismos_datos = models.BooleanField(default=True)
    facturacion_nombre = models.CharField(max_length=100, blank=True)
    facturacion_apellido = models.CharField(max_length=100, blank=True)
    facturacion_dni = models.CharField(max_length=20, blank=True)
    facturacion_cuit = models.CharField(max_length=20, blank=True)
    facturacion_razon_social = models.CharField(max_length=150, blank=True)
    facturacion_domicilio = models.CharField(max_length=255, blank=True)
    facturacion_condicion_iva = models.CharField(max_length=30, blank=True)
    facturacion_pais = models.CharField(max_length=100, blank=True)
    tipo_entrega = models.CharField(max_length=10, choices=ENTREGAS)
    receptor_mismos_datos = models.BooleanField(default=True)
    receptor_nombre = models.CharField(max_length=100, blank=True)
    receptor_apellido = models.CharField(max_length=100, blank=True)
    receptor_dni = models.CharField(max_length=20, blank=True)
    receptor_telefono = models.CharField(max_length=40, blank=True)
    envio_calle = models.CharField(max_length=120, blank=True)
    envio_altura = models.CharField(max_length=20, blank=True)
    envio_piso_departamento = models.CharField(max_length=60, blank=True)
    envio_localidad = models.CharField(max_length=100, blank=True)
    envio_provincia = models.CharField(max_length=100, blank=True)
    envio_codigo_postal = models.CharField(max_length=20, blank=True)
    envio_referencias = models.TextField(blank=True)
    medio_pago = models.CharField(max_length=15, choices=PAGOS)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    stock_reintegrado = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    producto_nombre = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto_nombre} × {self.cantidad}"


def comprobante_upload_to(instance, filename):
    from django.utils import timezone
    now = timezone.now()
    return f"comprobantes/{now:%Y/%m}/{filename}"


class ComprobanteTransferencia(BasicModel):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="comprobante")
    archivo = models.FileField(upload_to=comprobante_upload_to)
    nombre_original = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    tamanio = models.PositiveIntegerField()

    def __str__(self):
        return f"Comprobante {self.pedido.codigo}"


class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="historial")
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ["fecha", "pk"]
