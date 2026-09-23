from django.urls import reverse
from rest_framework import status

from api.tests.base import ApiBaseTestCase


class AuthApiTests(ApiBaseTestCase):
    def test_login_devuelve_token(self):
        response = self.client.post(
            reverse("api:login"),
            {"usuario": "cliente", "password": "Test12345!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["usuario"]["username"], "cliente")

    def test_me_requiere_autenticacion(self):
        response = self.client.get(reverse("api:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_devuelve_usuario_actual(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("api:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "cliente")
