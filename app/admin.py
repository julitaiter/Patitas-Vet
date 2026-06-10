from django.contrib import admin

from .models import Categoria, Producto, Servicio, Turno


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activa"]
    list_filter = ["activa"]
    search_fields = ["nombre"]


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria", "precio",
                    "duracion_minutos", "activo", "destacado"]
    list_filter = ["categoria", "activo", "destacado"]
    search_fields = ["nombre", "descripcion"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria",
                    "precio", "stock", "activo", "destacado"]
    list_filter = ["categoria", "activo", "destacado"]
    search_fields = ["nombre", "descripcion"]


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ["servicio", "usuario",
                    "mascota", "fecha", "hora", "estado"]
    list_filter = ["estado", "fecha", "servicio"]
    search_fields = ["usuario__username", "mascota", "servicio__nombre"]
