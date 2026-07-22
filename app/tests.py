from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto, Servicio


class CatalogoShoppingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="cliente",
            password="clave-segura-123",
        )
        categoria = Categoria.objects.create(nombre="Alimentos")
        cls.producto = Producto.objects.create(
            nombre="Alimento premium",
            descripcion="Alimento balanceado para perros adultos",
            precio=Decimal("15000.00"),
            categoria=categoria,
            activo=True,
            stock=3,
        )
        cls.producto_inactivo = Producto.objects.create(
            nombre="Producto discontinuado",
            descripcion="Ya no se vende",
            precio=Decimal("100.00"),
            categoria=categoria,
            activo=False,
            stock=10,
        )
        cls.producto_sin_stock = Producto.objects.create(
            nombre="Snack agotado",
            descripcion="Snack sin existencias",
            precio=Decimal("500.00"),
            categoria=categoria,
            activo=True,
            stock=0,
        )
        cls.servicio = Servicio.objects.create(
            nombre="Consulta alimentaria",
            descripcion="Asesoramiento sobre alimentación",
            precio=Decimal("9000.00"),
            categoria=categoria,
            activo=True,
            duracion_minutos=45,
        )

    def test_paginas_publicas_y_detalles_activos(self):
        for url in (
            reverse("detalle_producto", kwargs={"pk": self.producto.pk}),
            reverse("detalle_servicio", kwargs={"pk": self.servicio.pk}),
        ):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_detalle_no_expone_producto_inactivo(self):
        url = reverse("detalle_producto", kwargs={"pk": self.producto_inactivo.pk})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_productos_y_servicios_comparten_vista_de_detalle(self):
        producto_response = self.client.get(
            reverse("detalle_producto", kwargs={"pk": self.producto.pk})
        )
        servicio_response = self.client.get(
            reverse("detalle_servicio", kwargs={"pk": self.servicio.pk})
        )

        self.assertTemplateUsed(producto_response, "catalogo/detalle_item.html")
        self.assertTemplateUsed(servicio_response, "catalogo/detalle_item.html")
        self.assertEqual(producto_response.context["model"], "producto")
        self.assertEqual(servicio_response.context["model"], "servicio")
        self.assertContains(producto_response, "Iniciar sesión para comprar")
        self.assertNotContains(producto_response, "js-add-to-cart")
        self.assertContains(servicio_response, "Iniciar sesión para solicitar")

    def test_visitante_no_puede_acceder_a_acciones_del_carrito(self):
        carrito_url = reverse("ver_carrito")
        stock_url = reverse("validar_stock_producto", kwargs={"pk": self.producto.pk})
        catalogo_response = self.client.get(reverse("listar_catalogo"))

        self.assertRedirects(
            self.client.get(carrito_url),
            f"{reverse('account_login')}?next={carrito_url}",
        )
        self.assertRedirects(
            self.client.get(stock_url),
            f"{reverse('account_login')}?next={stock_url}",
        )
        self.assertNotContains(catalogo_response, 'id="cart-count"')
        self.assertNotContains(catalogo_response, "static/js/cart.js")
        self.assertNotContains(catalogo_response, "js-add-to-cart")

    def test_usuario_autenticado_puede_acceder_al_carrito(self):
        self.client.force_login(self.user)
        carrito_response = self.client.get(reverse("ver_carrito"))
        catalogo_response = self.client.get(reverse("listar_catalogo"))

        self.assertEqual(carrito_response.status_code, 200)
        self.assertContains(catalogo_response, 'id="cart-count"')
        self.assertContains(catalogo_response, "static/js/cart.js")
        self.assertContains(catalogo_response, "js-add-to-cart")

    def test_validar_stock_devuelve_datos_del_producto(self):
        self.client.force_login(self.user)
        url = reverse("validar_stock_producto", kwargs={"pk": self.producto.pk})
        response = self.client.get(url, {"cantidad": 3})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["producto"]["precio"], "15000.00")
        self.assertEqual(response.json()["producto"]["stock"], 3)

    def test_validar_stock_rechaza_cantidad_mayor_al_stock(self):
        self.client.force_login(self.user)
        url = reverse("validar_stock_producto", kwargs={"pk": self.producto.pk})
        response = self.client.get(url, {"cantidad": 4})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["ok"])

    def test_validar_stock_rechaza_producto_agotado_e_inactivo(self):
        self.client.force_login(self.user)
        agotado_url = reverse("validar_stock_producto", kwargs={"pk": self.producto_sin_stock.pk})
        inactivo_url = reverse("validar_stock_producto", kwargs={"pk": self.producto_inactivo.pk})

        self.assertFalse(self.client.get(agotado_url).json()["ok"])
        self.assertFalse(self.client.get(inactivo_url).json()["ok"])

    def test_autocomplete_incluye_productos_y_servicios_activos(self):
        response = self.client.get(reverse("buscar_catalogo_ajax"), {"term": "ali"})
        resultados = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["tipo"] for item in resultados}, {"Producto", "Servicio"})
        self.assertTrue(all(item["url"] for item in resultados))
        self.assertNotIn("Producto discontinuado", {item["value"] for item in resultados})

    def test_autocomplete_exige_dos_caracteres(self):
        response = self.client.get(reverse("buscar_catalogo_ajax"), {"term": "a"})
        self.assertEqual(response.json(), [])
