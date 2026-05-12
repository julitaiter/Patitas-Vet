from django.db import models


def catalogo_imagen_upload_to(instance, filename):
    """Guarda la imagen dentro de la carpeta plural del modelo.

    Ejemplos:
    - Servicio -> servicios/archivo.jpg
    - Producto -> productos/archivo.jpg
    """
    return f'{instance._meta.verbose_name_plural}/{filename}'


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.nombre


class ItemCatalogo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to=catalogo_imagen_upload_to, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.nombre


class Servicio(ItemCatalogo):
    class Meta:
        verbose_name = 'servicio'
        verbose_name_plural = 'servicios'


class Producto(ItemCatalogo):
    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
