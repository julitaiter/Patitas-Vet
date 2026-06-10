from django.contrib import admin
from .models import Consulta, Respuesta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'estado_respuesta', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('nombre', 'email', 'mensaje')

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('consulta', 'fecha')
    search_fields = ('consulta__nombre', 'consulta__email', 'mensaje')

