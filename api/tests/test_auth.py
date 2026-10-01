from django.urls import reverse
from rest_framework import status

from api.tests.base import ApiBaseTestCase


class AuthApiTests(ApiBaseTestCase):
    def test_registro_crea_usuario_y_devuelve_token(self):
        response = self.client.post(
            reverse("api:register"),
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "password": "ClaveSegura123!",
                "password_confirmacion": "ClaveSegura123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["usuario"]["username"], "nuevo")

    def test_registro_rechaza_email_duplicado_y_passwords_distintos(self):
        response = self.client.post(
            reverse("api:register"),
            {
                "username": "otro",
                "email": self.user.email.upper(),
                "password": "ClaveSegura123!",
                "password_confirmacion": "OtraClave123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

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

    def test_logout_invalida_token(self):
        login = self.client.post(
            reverse("api:login"),
            {"usuario": "cliente", "password": "Test12345!"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")

        response = self.client.post(reverse("api:logout"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            self.client.get(reverse("api:me")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
