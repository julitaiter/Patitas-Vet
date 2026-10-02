"""Carga datos de ejemplo para explorar el catálogo y solicitar turnos."""

from collections import Counter
from datetime import time
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from app.models import Categoria, DisponibilidadTurno, Producto, Sala, Servicio


CATEGORIAS = (
    "Servicios de salud",
    "Higiene y estética",
    "Alimentos",
    "Accesorios",
)

SERVICIOS = (
    {
        "nombre": "Consulta veterinaria",
        "descripcion": "Consulta general para evaluar la salud de tu mascota.",
        "precio": Decimal("18000.00"),
        "categoria": CATEGORIAS[0],
        "duracion_minutos": 30,
    },
    {
        "nombre": "Vacunación",
        "descripcion": "Turno para aplicar una vacuna según la indicación profesional.",
        "precio": Decimal("14000.00"),
        "categoria": CATEGORIAS[0],
        "duracion_minutos": 20,
    },
    {
        "nombre": "Baño y cuidado",
        "descripcion": "Baño y cuidados básicos de higiene para tu mascota.",
        "precio": Decimal("25000.00"),
        "categoria": CATEGORIAS[1],
        "duracion_minutos": 60,
    },
)

PRODUCTOS = (
    {
        "nombre": "Alimento para perros 3 kg",
        "descripcion": "Alimento balanceado de ejemplo para perros adultos.",
        "precio": Decimal("12000.00"),
        "categoria": CATEGORIAS[2],
        "stock": 12,
    },
    {
        "nombre": "Alimento para gatos 1 kg",
        "descripcion": "Alimento balanceado de ejemplo para gatos adultos.",
        "precio": Decimal("7500.00"),
        "categoria": CATEGORIAS[2],
        "stock": 15,
    },
    {
        "nombre": "Champú suave 250 ml",
        "descripcion": "Producto de higiene de ejemplo para mascotas.",
        "precio": Decimal("5500.00"),
        "categoria": CATEGORIAS[1],
        "stock": 8,
    },
    {
        "nombre": "Correa regulable",
        "descripcion": "Correa de ejemplo para paseos diarios.",
        "precio": Decimal("9000.00"),
        "categoria": CATEGORIAS[3],
        "stock": 10,
    },
)

SALAS = (
    ("Consultorio de atención", "Sala de ejemplo para consultas y vacunación."),
    ("Sala de cuidado", "Sala de ejemplo para baño y cuidado."),
)

DISPONIBILIDADES = (
    (SERVICIOS[0]["nombre"], SALAS[0][0], range(5), time(9), time(13), 30),
    (SERVICIOS[1]["nombre"], SALAS[0][0], range(5), time(14), time(17), 20),
    (SERVICIOS[2]["nombre"], SALAS[1][0], range(1, 6), time(9), time(15), 60),
)


class Command(BaseCommand):
    help = "Crea datos de ejemplo de catálogo, salas y disponibilidades sin modificar registros existentes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-existing",
            action="store_true",
            help="Permite agregar ejemplos faltantes cuando la base ya contiene datos.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        modelos = (Categoria, Producto, Servicio, Sala, DisponibilidadTurno)
        tiene_datos = any(modelo.objects.exists() for modelo in modelos)
        nombres_semilla = (
            (Categoria, CATEGORIAS),
            (Producto, tuple(item["nombre"] for item in PRODUCTOS)),
            (Servicio, tuple(item["nombre"] for item in SERVICIOS)),
            (Sala, tuple(nombre for nombre, _ in SALAS)),
        )
        semilla_presente = all(
            modelo.objects.filter(nombre=nombre).exists()
            for modelo, nombres in nombres_semilla
            for nombre in nombres
        )
        if tiene_datos and not semilla_presente and not options["allow_existing"]:
            raise CommandError(
                "La base ya contiene datos de catálogo o agenda. "
                "No se agregó nada. Usá --allow-existing para añadir solo ejemplos faltantes."
            )

        creados = Counter()
        categorias = {}
        servicios = {}
        salas = {}

        for nombre in CATEGORIAS:
            categoria, creada = Categoria.objects.get_or_create(nombre=nombre)
            categorias[nombre] = categoria
            creados["categorías"] += creada

        for datos in SERVICIOS:
            servicio = Servicio.objects.filter(nombre=datos["nombre"]).order_by("pk").first()
            if servicio is None:
                servicio = Servicio.objects.create(
                    nombre=datos["nombre"],
                    descripcion=datos["descripcion"],
                    precio=datos["precio"],
                    categoria=categorias[datos["categoria"]],
                    duracion_minutos=datos["duracion_minutos"],
                    destacado=datos["nombre"] == SERVICIOS[0]["nombre"],
                )
                creados["servicios"] += 1
            servicios[datos["nombre"]] = servicio

        for datos in PRODUCTOS:
            if not Producto.objects.filter(nombre=datos["nombre"]).exists():
                Producto.objects.create(
                    nombre=datos["nombre"],
                    descripcion=datos["descripcion"],
                    precio=datos["precio"],
                    categoria=categorias[datos["categoria"]],
                    stock=datos["stock"],
                )
                creados["productos"] += 1

        for nombre, descripcion in SALAS:
            sala = Sala.objects.filter(nombre=nombre).order_by("pk").first()
            if sala is None:
                sala = Sala.objects.create(nombre=nombre, descripcion=descripcion)
                creados["salas"] += 1
            salas[nombre] = sala

        for nombre_servicio, nombre_sala, dias, inicio, fin, intervalo in DISPONIBILIDADES:
            for dia in dias:
                # En bases pobladas no crear una franja que pise otra del mismo servicio y sala.
                if DisponibilidadTurno.objects.filter(
                    servicio=servicios[nombre_servicio],
                    sala=salas[nombre_sala],
                    dia_semana=dia,
                    hora_inicio__lt=fin,
                    hora_fin__gt=inicio,
                ).exists():
                    continue
                _, creada = DisponibilidadTurno.objects.get_or_create(
                    servicio=servicios[nombre_servicio],
                    sala=salas[nombre_sala],
                    dia_semana=dia,
                    hora_inicio=inicio,
                    hora_fin=fin,
                    defaults={"intervalo_minutos": intervalo},
                )
                creados["disponibilidades"] += creada

        self.stdout.write(self.style.SUCCESS(
            "Bootstrap de ejemplo listo. Registros creados: "
            + ", ".join(
                f"{tipo}={creados[tipo]}"
                for tipo in ("categorías", "productos", "servicios", "salas", "disponibilidades")
            )
            + ". No se modificaron registros existentes."
        ))
