from django.shortcuts import render
from .models import Servicio, Producto


def index(request):
    servicios = Servicio.objects.all()[:3]

    return render(request, 'index.html', {
        'servicios': servicios
    })


def servicios(request):
    servicios = Servicio.objects.all()
    productos = Producto.objects.all()

    return render(request, 'servicios.html', {
        'servicios': servicios,
        'productos': productos
    })