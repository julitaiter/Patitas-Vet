from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from app.models import Turno
from api.tests.base import ApiBaseTestCase


class TurnosApiTests(ApiBaseTestCase):
    def setUp(self):
        super().setUp()
        fecha = timezone.localdate() + timedelta(days=1)
        # Asegura que la fecha elegida tenga disponibilidades en ambas salas.
        self.fecha = fecha
        self.crear_disponibilidad(self.sala_a, fecha.weekday())
        self.crear_disponibilidad(self.sala_b, fecha.weekday())

    def test_cliente_crea_turno_y_sala_se_asigna(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("api:turno-list"),
            {
                "servicio": self.servicio.pk,
                "fecha": self.fecha.isoformat(),
                "hora": "09:30",
                "mascota": "Firulais",
                "observaciones": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        turno = Turno.objects.get(usuario=self.user)
        self.assertIn(turno.sala_id, {self.sala_a.pk, self.sala_b.pk})

    def test_sala_ocupada_se_excluye(self):
        Turno.objects.create(
            usuario=self.staff,
            servicio=self.servicio,
            sala=self.sala_a,
            fecha=self.fecha,
            hora="10:00",
            mascota="Ocupado",
            estado=Turno.ESTADO_CONFIRMADO,
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("api:turno-list"),
            {
                "servicio": self.servicio.pk,
                "fecha": self.fecha.isoformat(),
                "hora": "10:00",
                "mascota": "Michi",
                "observaciones": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Turno.objects.get(usuario=self.user).sala_id, self.sala_b.pk)

    def test_cliente_solo_lista_sus_turnos(self):
        Turno.objects.create(
            usuario=self.staff,
            servicio=self.servicio,
            sala=self.sala_a,
            fecha=self.fecha,
            hora="11:00",
            mascota="Otro",
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("api:turno-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_staff_puede_confirmar(self):
        turno = Turno.objects.create(
            usuario=self.user,
            servicio=self.servicio,
            sala=self.sala_a,
            fecha=self.fecha,
            hora="11:30",
            mascota="Firulais",
        )
        self.client.force_authenticate(self.staff)
        response = self.client.post(reverse("api:turno-confirmar", kwargs={"pk": turno.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        turno.refresh_from_db()
        self.assertEqual(turno.estado, Turno.ESTADO_CONFIRMADO)
