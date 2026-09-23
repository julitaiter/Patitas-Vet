from django.urls import reverse
from rest_framework import status

from api.tests.base import ApiBaseTestCase


class CatalogoApiTests(ApiBaseTestCase):
    def test_productos_publicos(self):
        response = self.client.get(reverse("api:producto-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stock_valida_cantidad(self):
        url = reverse("api:producto-stock", kwargs={"pk": self.producto.pk})
        response = self.client.get(url, {"cantidad": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

        response = self.client.get(url, {"cantidad": 99})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(response.data["ok"])

    def test_busqueda_combina_productos_y_servicios(self):
        response = self.client.get(reverse("api:buscar"), {"q": "Consulta"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["tipo"] == "servicio" for item in response.data["results"]))

    def test_cliente_no_puede_crear_producto(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("api:producto-list"),
            {
                "nombre": "Nuevo",
                "descripcion": "x",
                "precio": "100.00",
                "stock": 1,
                "categoria": self.categoria.pk,
                "activo": True,
                "destacado": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
