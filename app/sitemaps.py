from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Producto, Servicio


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ("index", "listar_catalogo", "preguntas_frecuentes")

    def location(self, item):
        return reverse(item)


class ProductoSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Producto.objects.filter(activo=True).order_by("pk")

    def location(self, item):
        return reverse("detalle_producto", kwargs={"pk": item.pk})

    def lastmod(self, item):
        return item.updated_at


class ServicioSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Servicio.objects.filter(activo=True).order_by("pk")

    def location(self, item):
        return reverse("detalle_servicio", kwargs={"pk": item.pk})

    def lastmod(self, item):
        return item.updated_at
