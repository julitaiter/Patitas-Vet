from django.conf import settings
from django.db import models


def catalogo_imagen_upload_to(instance, filename):
    return f"{instance._meta.verbose_name_plural}/{filename}"


class BasicModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Categoria(BasicModel):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Sala(BasicModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "sala"
        verbose_name_plural = "salas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ItemCatalogo(BasicModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(
        upload_to=catalogo_imagen_upload_to, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Servicio(ItemCatalogo):
    sala = models.ForeignKey(
        Sala,
        on_delete=models.PROTECT,
        related_name="servicios",
        blank=True,
        null=True
    )
    duracion_minutos = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"


class Producto(ItemCatalogo):
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"


class DisponibilidadTurno(BasicModel):
    DIA_LUNES = 0
    DIA_MARTES = 1
    DIA_MIERCOLES = 2
    DIA_JUEVES = 3
    DIA_VIERNES = 4
    DIA_SABADO = 5
    DIA_DOMINGO = 6

    DIAS_SEMANA = [
        (DIA_LUNES, "Lunes"),
        (DIA_MARTES, "Martes"),
        (DIA_MIERCOLES, "Miércoles"),
        (DIA_JUEVES, "Jueves"),
        (DIA_VIERNES, "Viernes"),
        (DIA_SABADO, "Sábado"),
        (DIA_DOMINGO, "Domingo"),
    ]

    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    intervalo_minutos = models.PositiveIntegerField(default=30)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "disponibilidad de turno"
        verbose_name_plural = "disponibilidades de turnos"
        ordering = ["sala", "dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["sala", "dia_semana", "hora_inicio", "hora_fin"],
                name="disponibilidad_unica_por_sala_dia_horario",
            )
        ]

    def __str__(self):
        return f"{self.sala} - {self.get_dia_semana_display()} {self.hora_inicio} a {self.hora_fin}"


class Turno(BasicModel):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_CONFIRMADO = "confirmado"
    ESTADO_CANCELADO = "cancelado"
    ESTADO_REALIZADO = "realizado"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_CONFIRMADO, "Confirmado"),
        (ESTADO_CANCELADO, "Cancelado"),
        (ESTADO_REALIZADO, "Realizado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name="turnos", blank=True, null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    mascota = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
    )

    class Meta:
        verbose_name = "turno"
        verbose_name_plural = "turnos"
        ordering = ["fecha", "hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["sala", "fecha", "hora"],
                name="turno_unico_por_sala_fecha_hora",
            )
        ]

    def __str__(self):
        return f"{self.servicio} - {self.fecha} {self.hora}"
