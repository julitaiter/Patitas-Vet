from django.contrib import admin
from .models import Consulta, Respuesta


class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 0

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'estado_respuesta', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('nombre', 'email', 'mensaje')
    inlines = [RespuestaInline]
