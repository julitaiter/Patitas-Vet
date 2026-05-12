from django.contrib import admin
from .models import Categoria, Servicio, Producto

admin.site.register(Categoria)
admin.site.register(Servicio)
admin.site.register(Producto)