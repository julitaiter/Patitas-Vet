from django.urls import reverse
from rest_framework import status

from contacto.models import Consulta, Respuesta
from api.tests.base import ApiBaseTestCase


class ContactoApiTests(ApiBaseTestCase):
    def test_visitante_puede_crear_consulta_pero_no_listarlas(self):
        response = self.client.post(
            reverse("api:consulta-list"),
            {
                "nombre": "Ana",
                "email": "ana@example.com",
                "telefono": "123456",
                "mensaje": "Necesito información",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 1)
        self.assertEqual(
            self.client.get(reverse("api:consulta-list")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_staff_responde_consulta_y_actualiza_estado(self):
        consulta = Consulta.objects.create(
            nombre="Ana",
            email="ana@example.com",
            mensaje="Consulta",
        )
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("api:respuesta-list"),
            {"consulta": consulta.pk, "mensaje": "Respuesta"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Respuesta.objects.filter(consulta=consulta).exists())
        consulta.refresh_from_db()
        self.assertEqual(consulta.estado, Consulta.CONTESTADA)
