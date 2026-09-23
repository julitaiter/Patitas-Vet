from datetime import time

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app.models import Categoria, DisponibilidadTurno, Producto, Sala, Servicio


User = get_user_model()


class ApiBaseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="Test12345!",
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="Test12345!",
            is_staff=True,
        )
        self.categoria = Categoria.objects.create(nombre="Veterinaria", activa=True)
        self.servicio = Servicio.objects.create(
            nombre="Consulta",
            descripcion="Consulta veterinaria",
            precio="12000.00",
            categoria=self.categoria,
            activo=True,
            destacado=True,
            duracion_minutos=30,
        )
        self.producto = Producto.objects.create(
            nombre="Alimento",
            descripcion="Alimento premium",
            precio="15000.00",
            categoria=self.categoria,
            activo=True,
            destacado=False,
            stock=5,
        )
        self.sala_a = Sala.objects.create(nombre="Consultorio A", activa=True)
        self.sala_b = Sala.objects.create(nombre="Consultorio B", activa=True)

    def crear_disponibilidad(self, sala, dia_semana):
        return DisponibilidadTurno.objects.create(
            servicio=self.servicio,
            sala=sala,
            dia_semana=dia_semana,
            hora_inicio=time(9, 0),
            hora_fin=time(12, 0),
            intervalo_minutos=30,
            activa=True,
        )
