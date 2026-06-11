from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


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
    duracion_minutos = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"


class Producto(ItemCatalogo):
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"


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
    fecha = models.DateField()
    hora = models.TimeField()
    mascota = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)

    class Meta:
        verbose_name = "turno"
        verbose_name_plural = "turnos"
        ordering = ["fecha", "hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["servicio", "fecha", "hora"],
                name="turno_unico_por_servicio_fecha_hora",
            )
        ]

    def __str__(self):
        return f"{self.servicio} - {self.fecha} {self.hora}"
