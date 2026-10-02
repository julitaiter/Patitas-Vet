import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.test import RequestFactory
from django.urls import reverse

from .forms_checkout import CheckoutForm
from .models import Categoria, ConfiguracionCheckout, CuentaTransferencia, Pedido, Producto
from .admin import PedidoAdmin
from .services.pedidos import PedidoError, calcular_costo_envio, cancelar_pedido, crear_pedido


def datos_checkout(**overrides):
    data = dict(comprador_nombre="Ana", comprador_apellido="Paz", comprador_email="ana@example.com",
                comprador_telefono="11111111", comprador_dni="12345678", tipo_factura="B",
                facturacion_mismos_datos=True, tipo_entrega="envio", receptor_mismos_datos=True,
                envio_calle="Calle", envio_altura="12", envio_localidad="Ciudad",
                envio_provincia="Buenos Aires", envio_codigo_postal="1000",
                medio_pago="efectivo", cart_payload='[{"id": 1, "cantidad": 1}]')
    data.update(overrides)
    return data


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="clave1234", email="ana@example.com")
        self.other = get_user_model().objects.create_user(username="otra", password="clave1234")
        self.categoria = Categoria.objects.create(nombre="Alimentos")
        self.producto = Producto.objects.create(nombre="Alimento", descripcion="Bolsa", precio=Decimal("1000.00"), stock=2, categoria=self.categoria)
        self.config = ConfiguracionCheckout.objects.create(nombre_tienda="Tienda", direccion_tienda="Calle 1", email_negocio="vet@example.com")
        self.cart = [{"id": self.producto.pk, "cantidad": 1}]

    @patch("app.services.pedidos.enviar_emails_pedido")
    def test_creacion_snapshot_totales_codigo_y_stock(self, enviar):
        with self.captureOnCommitCallbacks(execute=True):
            pedido = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        self.assertRegex(pedido.codigo, r"^\d{14}$")
        self.assertEqual((pedido.subtotal, pedido.costo_envio, pedido.total), (Decimal("1000"), Decimal("4000"), Decimal("5000")))
        self.assertEqual(pedido.items.first().producto_nombre, "Alimento")
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 1)
        self.assertEqual(pedido.historial.count(), 2)
        enviar.assert_called_once_with(pedido.pk)

    def test_stock_insuficiente_no_crea_pedido(self):
        with self.assertRaises(PedidoError):
            crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=[{"id": self.producto.pk, "cantidad": 3}], configuracion=self.config)
        self.assertFalse(Pedido.objects.exists())
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)

    def test_carrito_no_confia_en_precio_ni_acepta_duplicados(self):
        pedido = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=[{"id": self.producto.pk, "cantidad": 1, "precio": 1, "nombre": "Falso"}], configuracion=self.config)
        self.assertEqual(pedido.items.first().precio_unitario, Decimal("1000"))
        with self.assertRaises(PedidoError):
            crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart + self.cart, configuracion=self.config)
        with self.assertRaises(PedidoError):
            crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=[{"id": self.producto.pk, "cantidad": 0}], configuracion=self.config)

    def test_opciones_no_configuradas_no_se_aceptan(self):
        self.config.nombre_tienda = ""
        self.config.direccion_tienda = ""
        self.assertFalse(CheckoutForm(datos_checkout(tipo_entrega="retiro"), configuracion=self.config).is_valid())
        self.assertTrue(CheckoutForm(datos_checkout(tipo_entrega="envio"), configuracion=self.config).is_valid())
        self.assertFalse(CheckoutForm(datos_checkout(medio_pago="transferencia"), configuracion=self.config).is_valid())

    def test_reintegro_idempotente(self):
        pedido = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        cancelar_pedido(pedido, self.user)
        cancelar_pedido(pedido, self.user)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)
        self.assertEqual(pedido.historial.count(), 3)

    def test_admin_cancela_y_reintegra_stock(self):
        staff = get_user_model().objects.create_superuser(username="admin-pedidos", password="clave1234", email="admin@example.com")
        pedido = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        request = RequestFactory().post(reverse("admin:app_pedido_change", args=[pedido.pk]))
        request.user = staff
        pedido.estado = "cancelado"
        PedidoAdmin(Pedido, AdminSite()).save_model(request, pedido, None, True)
        pedido.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(pedido.estado, "cancelado")
        self.assertTrue(pedido.stock_reintegrado)
        self.assertEqual(self.producto.stock, 2)

    def test_envio_gratis_y_retiro(self):
        self.config.envio_gratis_desde = Decimal("1000")
        self.assertEqual(calcular_costo_envio(Decimal("1000"), "envio", self.config), 0)
        self.assertEqual(calcular_costo_envio(Decimal("10"), "retiro", self.config), 0)

    def test_facturas_y_direccion_condicional(self):
        self.assertTrue(CheckoutForm(datos_checkout(), configuracion=self.config).is_valid())
        self.assertFalse(CheckoutForm(datos_checkout(facturacion_mismos_datos=False), configuracion=self.config).is_valid())
        self.assertFalse(CheckoutForm(datos_checkout(tipo_factura="A"), configuracion=self.config).is_valid())
        ae = dict(facturacion_cuit="30123456789", facturacion_razon_social="Empresa", facturacion_domicilio="Calle 1", facturacion_condicion_iva="exento")
        factura_a = CheckoutForm(datos_checkout(tipo_factura="A", **ae), configuracion=self.config)
        self.assertTrue(factura_a.is_valid())
        self.assertEqual(factura_a.cleaned_data["facturacion_pais"], "Argentina")
        self.assertFalse(factura_a.cleaned_data["facturacion_mismos_datos"])
        self.assertFalse(CheckoutForm(datos_checkout(tipo_factura="E", facturacion_pais="ARGENTINA", **ae), configuracion=self.config).is_valid())
        self.assertTrue(CheckoutForm(datos_checkout(tipo_factura="E", facturacion_pais="Chile", **ae), configuracion=self.config).is_valid())
        self.assertFalse(CheckoutForm(datos_checkout(envio_calle=""), configuracion=self.config).is_valid())
        self.assertFalse(CheckoutForm(datos_checkout(receptor_mismos_datos=False), configuracion=self.config).is_valid())

    def test_transferencia_y_comprobante(self):
        cuenta = CuentaTransferencia.objects.create(banco="Banco", titular="Vet", cuit="1", alias="vet", cbu_cvu="123", tipo_cuenta="CA", principal=True)
        self.assertFalse(CheckoutForm(datos_checkout(medio_pago="transferencia"), configuracion=self.config, cuenta=cuenta).is_valid())
        archivo = SimpleUploadedFile("comprobante.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        self.assertTrue(CheckoutForm(datos_checkout(medio_pago="transferencia"), {"comprobante": archivo}, configuracion=self.config, cuenta=cuenta).is_valid())
        malo = SimpleUploadedFile("comprobante.exe", b"bad", content_type="application/octet-stream")
        self.assertFalse(CheckoutForm(datos_checkout(medio_pago="transferencia"), {"comprobante": malo}, configuracion=self.config, cuenta=cuenta).is_valid())
        self.config.comprobante_max_mb = 1
        grande = SimpleUploadedFile("comprobante.pdf", b"%PDF-" + b"x" * (1024 * 1024 + 1), content_type="application/pdf")
        self.assertFalse(CheckoutForm(datos_checkout(medio_pago="transferencia"), {"comprobante": grande}, configuracion=self.config, cuenta=cuenta).is_valid())

    def test_checkout_login_y_propiedad_pedido(self):
        self.assertIn("/accounts/login/", self.client.get(reverse("checkout")).url)
        self.client.force_login(self.user)
        pedido = crear_pedido(usuario=self.other, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        self.assertEqual(self.client.get(reverse("checkout") + f"?pedido={pedido.codigo}").status_code, 404)

    def test_carrito_ofrece_enlace_a_checkout(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(reverse("ver_carrito"))
        self.assertContains(respuesta, 'id="cart-checkout-actions"')
        self.assertContains(respuesta, f'href="{reverse("checkout")}"')

    def test_checkout_agrupa_pasos_y_muestra_labels_legibles(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(reverse("checkout"))
        self.assertContains(respuesta, 'data-step="0"')
        self.assertContains(respuesta, 'data-step="3"')
        self.assertNotContains(respuesta, 'data-step="4"')
        self.assertContains(respuesta, 'Quiero solicitar Factura A o E')
        self.assertContains(respuesta, 'type="radio" name="tipo_entrega"')
        self.assertContains(respuesta, 'Correo electrónico')
        self.assertContains(respuesta, 'Código postal')
        self.assertContains(respuesta, 'Comprobante de transferencia')

    def test_entrega_requiere_eleccion_explicita(self):
        self.client.force_login(self.user)
        respuesta = self.client.get(reverse("checkout"))
        html = respuesta.content.decode()
        self.assertIn("Retiro en tienda", html)
        self.assertNotIn('name="tipo_entrega" value="retiro" checked', html)
        self.assertNotIn('name="tipo_entrega" value="envio" checked', html)
        self.assertFalse(CheckoutForm(datos_checkout(tipo_entrega=""), configuracion=self.config).is_valid())

    def test_mis_pedidos_requiere_login_y_muestra_estado_vacio(self):
        self.assertIn("/accounts/login/", self.client.get(reverse("mis_pedidos")).url)
        self.client.force_login(self.user)
        respuesta = self.client.get(reverse("mis_pedidos"))
        self.assertContains(respuesta, "Aún no tenés pedidos")
        self.assertContains(respuesta, "Mis pedidos")

    def test_mis_pedidos_solo_muestra_los_propios_y_detalle_protegido(self):
        propio = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        ajeno = crear_pedido(usuario=self.other, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        self.client.force_login(self.user)
        listado = self.client.get(reverse("mis_pedidos"))
        self.assertContains(listado, propio.codigo)
        self.assertNotContains(listado, ajeno.codigo)
        self.assertContains(listado, reverse("detalle_pedido", args=[propio.codigo]))
        detalle = self.client.get(reverse("detalle_pedido", args=[propio.codigo]))
        self.assertContains(detalle, "Alimento")
        self.assertContains(detalle, "Total")
        self.assertNotContains(detalle, "Cancelar pedido")
        self.assertEqual(self.client.get(reverse("detalle_pedido", args=[ajeno.codigo])).status_code, 404)
        self.client.logout()
        self.assertIn("/accounts/login/", self.client.get(reverse("detalle_pedido", args=[propio.codigo])).url)

    def test_perfil_y_menu_enlazan_mis_pedidos(self):
        self.client.force_login(self.user)
        perfil = self.client.get(reverse("mi_perfil"))
        self.assertContains(perfil, reverse("mis_pedidos"))
        self.assertContains(perfil, "Pedidos recientes")

    def test_draft_y_confirmacion(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("checkout"), {"action": "save_draft", "comprador_nombre": "Borrador"}).json(), {"ok": True})
        self.assertContains(self.client.get(reverse("checkout")), "Borrador")
        data = datos_checkout(cart_payload=json.dumps(self.cart))
        response = self.client.post(reverse("checkout"), data)
        self.assertEqual(response.status_code, 302)
        self.assertIn("?pedido=", response.url)
        self.assertContains(self.client.get(response.url), "Pedido recibido")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_emails_cliente_y_negocio(self):
        from .services.pedidos import enviar_emails_pedido
        pedido = crear_pedido(usuario=self.user, datos=datos_checkout(), carrito=self.cart, configuracion=self.config)
        enviar_emails_pedido(pedido.pk)
        self.assertEqual({email.to[0] for email in mail.outbox}, {"ana@example.com", "vet@example.com"})
