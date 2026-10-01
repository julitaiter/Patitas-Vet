from django.urls import reverse
from rest_framework import status

from app.models import Turno
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

    def test_eliminacion_protegida_devuelve_conflicto(self):
        self.crear_disponibilidad(self.sala_a, 0)
        Turno.objects.create(
            usuario=self.user,
            servicio=self.servicio,
            sala=self.sala_a,
            fecha="2030-01-07",
            hora="09:00",
            mascota="Luna",
        )
        self.client.force_authenticate(self.staff)

        response = self.client.delete(
            reverse("api:sala-detail", kwargs={"pk": self.sala_a.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_documentacion_es_publica(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(
            self.client.get(reverse("api:schema")).status_code,
            status.HTTP_200_OK,
        )
