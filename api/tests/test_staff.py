from django.urls import reverse
from rest_framework import status

from api.tests.base import ApiBaseTestCase


class StaffApiTests(ApiBaseTestCase):
    def test_salas_son_privadas_para_staff(self):
        response = self.client.get(reverse("api:sala-list"))
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("api:sala-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_puede_crear_categoria(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            reverse("api:categoria-list"),
            {"nombre": "Accesorios", "activa": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
