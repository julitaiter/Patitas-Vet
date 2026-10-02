from datetime import date, time
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .models import Categoria, DisponibilidadTurno, Producto, Sala, Servicio
from .services.turnos import obtener_horarios_disponibles


class BootstrapInicialTests(TestCase):
    def ejecutar(self, *args):
        salida = StringIO()
        call_command("bootstrap_inicial", *args, stdout=salida)
        return salida.getvalue()

    def test_crea_catalogo_y_agenda_utilizable(self):
        salida = self.ejecutar()

        self.assertIn("categorías=4", salida)
        self.assertEqual(Categoria.objects.count(), 4)
        self.assertEqual(Producto.objects.count(), 4)
        self.assertEqual(Servicio.objects.count(), 3)
        self.assertEqual(Sala.objects.count(), 2)
        self.assertEqual(DisponibilidadTurno.objects.count(), 15)
        self.assertTrue(Producto.objects.filter(activo=True, stock__gt=0).exists())
        self.assertTrue(Servicio.objects.filter(activo=True, destacado=True).exists())

        consulta = Servicio.objects.get(nombre="Consulta veterinaria")
        lunes = date(2026, 10, 5)
        self.assertIn(time(9, 0), obtener_horarios_disponibles(consulta, lunes))
        self.assertIn(time(9, 30), obtener_horarios_disponibles(consulta, lunes))

    def test_repetir_no_duplica_ni_sobrescribe(self):
        self.ejecutar()
        producto = Producto.objects.get(nombre="Correa regulable")
        producto.precio = Decimal("12345.00")
        producto.save(update_fields=["precio"])
        historial_antes = producto.history.count()

        salida = self.ejecutar()

        self.assertIn("productos=0", salida)
        self.assertEqual(Producto.objects.count(), 4)
        self.assertEqual(Servicio.objects.count(), 3)
        self.assertEqual(DisponibilidadTurno.objects.count(), 15)
        producto.refresh_from_db()
        self.assertEqual(producto.precio, Decimal("12345.00"))
        self.assertEqual(producto.history.count(), historial_antes)

    def test_base_con_datos_exige_opcion_explicita(self):
        Categoria.objects.create(nombre="Categoría real")

        with self.assertRaisesMessage(CommandError, "--allow-existing"):
            self.ejecutar()
        self.assertEqual(Categoria.objects.count(), 1)
        self.assertFalse(Producto.objects.exists())

        self.ejecutar("--allow-existing")
        self.assertTrue(Categoria.objects.filter(nombre="Categoría real").exists())
        self.assertEqual(Categoria.objects.count(), 5)
        self.assertEqual(Producto.objects.count(), 4)

    def test_no_superpone_disponibilidad_existente(self):
        self.ejecutar()
        servicio = Servicio.objects.get(nombre="Consulta veterinaria")
        sala = Sala.objects.get(nombre="Consultorio de atención")
        DisponibilidadTurno.objects.filter(
            servicio=servicio, sala=sala, dia_semana=0,
        ).delete()
        DisponibilidadTurno.objects.create(
            servicio=servicio, sala=sala, dia_semana=0,
            hora_inicio=time(8), hora_fin=time(12), intervalo_minutos=30,
        )

        self.ejecutar("--allow-existing")

        self.assertEqual(DisponibilidadTurno.objects.filter(
            servicio=servicio, sala=sala, dia_semana=0,
        ).count(), 1)
