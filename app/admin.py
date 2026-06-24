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

def confirmar_turno(modeladmin, request, queryset):
    queryset.update(estado=Turno.ESTADO_CONFIRMADO)

def cancelar_turno(modeladmin, request, queryset):
    queryset.update(estado=Turno.ESTADO_CANCELADO)

def realizar_turno(modeladmin, request, queryset):
    queryset.update(estado=Turno.ESTADO_REALIZADO)
realizar_turno.short_description = "Marcar como realizado"

def marcar_turno_pendiente(modeladmin, request, queryset):
    queryset.update(estado=Turno.ESTADO_PENDIENTE)
marcar_turno_pendiente.short_description = "Marcar como pendiente"

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ["servicio", "usuario",
                    "mascota", "fecha", "hora", "estado"]
    actions = [confirmar_turno, cancelar_turno, realizar_turno, marcar_turno_pendiente]
    list_filter = ["estado", "fecha", "servicio"]
    search_fields = ["usuario__username", "mascota", "servicio__nombre"]
