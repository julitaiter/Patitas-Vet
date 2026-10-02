from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, ConfiguracionCheckout, Producto, Servicio
from .services.pedidos import cancelar_pedido, crear_pedido
from .tests_checkout import datos_checkout


class CatalogoHistoryTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Consulta")

    def test_producto_guarda_creacion_cambios_y_eliminacion(self):
        producto = Producto.objects.create(
            nombre="Alimento", descripcion="Bolsa", precio=Decimal("100.00"),
            categoria=self.categoria, stock=5,
        )
        producto_id = producto.pk
        self.assertEqual(producto.history.get().history_type, "+")

        producto.precio = Decimal("120.00")
        producto.save(update_fields=["precio"])
        self.assertEqual(producto.history.first().precio, Decimal("120.00"))

        producto.stock = 3
        producto.save(update_fields=["stock"])
        self.assertEqual(producto.history.first().stock, 3)

        producto.activo = False
        producto.save(update_fields=["activo"])
        cambio = producto.history.first()
        self.assertEqual(cambio.history_type, "~")
        self.assertFalse(cambio.activo)

        producto.delete()
        self.assertEqual(
            list(Producto.history.filter(id=producto_id).values_list("history_type", flat=True)),
            ["-", "~", "~", "~", "+"],
        )

    def test_servicio_guarda_creacion_cambio_y_eliminacion(self):
        servicio = Servicio.objects.create(
            nombre="Consulta", descripcion="General", precio=Decimal("200.00"),
            categoria=self.categoria, duracion_minutos=30,
        )
        servicio_id = servicio.pk
        servicio.duracion_minutos = 45
        servicio.save(update_fields=["duracion_minutos"])
        self.assertEqual(servicio.history.first().duracion_minutos, 45)
        servicio.delete()
        self.assertEqual(
            list(Servicio.history.filter(id=servicio_id).values_list("history_type", flat=True)),
            ["-", "~", "+"],
        )

    def test_no_se_audita_categoria(self):
        self.assertFalse(hasattr(Categoria, "history"))

    def test_admin_muestra_historial_y_atribuye_accion_masiva(self):
        staff = get_user_model().objects.create_superuser(
            username="auditor", email="auditor@example.com", password="clave-segura-123",
        )
        producto = Producto.objects.create(
            nombre="Alimento", descripcion="Bolsa", precio=Decimal("100.00"),
            categoria=self.categoria, stock=5,
        )
        servicio = Servicio.objects.create(
            nombre="Consulta", descripcion="General", precio=Decimal("200.00"),
            categoria=self.categoria,
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("admin:app_producto_history", args=[producto.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:app_servicio_history", args=[servicio.pk])).status_code, 200)
        self.client.logout()
        self.assertNotEqual(self.client.get(reverse("admin:app_producto_history", args=[producto.pk])).status_code, 200)
        self.client.force_login(staff)

        response = self.client.post(reverse("admin:app_producto_changelist"), {
            "action": "desactivar_items", "_selected_action": [producto.pk], "select_across": "0",
        })
        self.assertEqual(response.status_code, 302)
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        self.assertEqual(producto.history.first().history_user, staff)

    def test_checkout_y_cancelacion_auditan_stock(self):
        usuario = get_user_model().objects.create_user(username="cliente", password="clave-segura-123")
        producto = Producto.objects.create(
            nombre="Alimento", descripcion="Bolsa", precio=Decimal("100.00"),
            categoria=self.categoria, stock=2,
        )
        configuracion = ConfiguracionCheckout.objects.create(
            nombre_tienda="Tienda", direccion_tienda="Calle 1", email_negocio="vet@example.com",
        )
        pedido = crear_pedido(
            usuario=usuario, datos=datos_checkout(),
            carrito=[{"id": producto.pk, "cantidad": 1}], configuracion=configuracion,
        )
        self.assertEqual(producto.history.first().stock, 1)
        cancelar_pedido(pedido, usuario)
        self.assertEqual(
            list(producto.history.values_list("stock", flat=True)), [2, 1, 2],
        )
