from .forms import ServicioForm, ProductoForm
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from .models import Servicio, Producto
from .forms import ItemCatalogoForm, ServicioForm


def index(request):
    servicios_destacados = (
        Servicio.objects
        .select_related("categoria")
        .order_by("nombre")[:3]
    )

    return render(request, "index.html", {
        "servicios_destacados": servicios_destacados,
    })


def listar_catalogo(request):
    servicios = Servicio.objects.all().order_by("nombre")
    productos = Producto.objects.all().order_by("nombre")

    return render(request, "catalogo/list.html", {
        "servicios": servicios,
        "productos": productos,
    })


def get_item_config(model):
    configs = {
        "servicio": {
            "form_class": ServicioForm,
            "titulo": "Agregar servicio",
            "submit": "Guardar servicio",
        },
        "producto": {
            "form_class": ProductoForm,
            "titulo": "Agregar producto",
            "submit": "Guardar producto",
        },
    }

    return configs.get(model)


@staff_member_required
def nuevo_item(request, model):
    config = get_item_config(model)

    if config is None:
        return redirect("listar_catalogo")

    form_class = config["form_class"]

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("listar_catalogo")
    else:
        form = form_class()

    return render(request, "catalogo/form_item.html", {
        "form": form,
        "titulo": config["titulo"],
        "submit": config["submit"],
        "model": model,
    })
