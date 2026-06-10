from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm, ServicioForm, TurnoForm
from .models import Categoria, Producto, Servicio, Turno


def index(request):
    servicios_destacados = (
        Servicio.objects
        .select_related("categoria")
        .filter(activo=True, destacado=True)
        .order_by("nombre")[:3]
    )

    if not servicios_destacados:
        servicios_destacados = (
            Servicio.objects
            .select_related("categoria")
            .filter(activo=True)
            .order_by("nombre")[:3]
        )

    return render(request, "index.html", {
        "servicios_destacados": servicios_destacados,
    })


def listar_catalogo(request):
    query = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    categoria_id_int = int(categoria_id) if categoria_id.isdigit() else None

    servicios = Servicio.objects.select_related(
        "categoria").filter(activo=True)
    productos = Producto.objects.select_related(
        "categoria").filter(activo=True)
    categorias = Categoria.objects.filter(activa=True).order_by("nombre")

    if query:
        servicios = servicios.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    if categoria_id_int:
        servicios = servicios.filter(categoria_id=categoria_id_int)
        productos = productos.filter(categoria_id=categoria_id_int)

    return render(request, "catalogo/list.html", {
        "servicios": servicios.order_by("nombre"),
        "productos": productos.order_by("nombre"),
        "categorias": categorias,
        "query": query,
        "categoria_id": categoria_id_int,
    })


def get_item_config(model):
    configs = {
        "servicio": {
            "model_class": Servicio,
            "form_class": ServicioForm,
            "titulo_crear": "Agregar servicio",
            "titulo_editar": "Editar servicio",
            "submit_crear": "Guardar servicio",
            "submit_editar": "Actualizar servicio",
        },
        "producto": {
            "model_class": Producto,
            "form_class": ProductoForm,
            "titulo_crear": "Agregar producto",
            "titulo_editar": "Editar producto",
            "submit_crear": "Guardar producto",
            "submit_editar": "Actualizar producto",
        },
    }

    return configs.get(model)


@staff_member_required
def nuevo_item(request, model):
    config = get_item_config(model)

    if config is None:
        messages.error(request, "Tipo de ítem inválido.")
        return redirect("listar_catalogo")

    form_class = config["form_class"]

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Ítem creado correctamente.")
            return redirect("listar_catalogo")
    else:
        form = form_class()

    return render(request, "catalogo/form_item.html", {
        "form": form,
        "titulo": config["titulo_crear"],
        "submit": config["submit_crear"],
    })


@staff_member_required
def editar_item(request, model, pk):
    config = get_item_config(model)

    if config is None:
        messages.error(request, "Tipo de ítem inválido.")
        return redirect("listar_catalogo")

    obj = get_object_or_404(config["model_class"], pk=pk)
    form_class = config["form_class"]

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Ítem actualizado correctamente.")
            return redirect("listar_catalogo")
    else:
        form = form_class(instance=obj)

    return render(request, "catalogo/form_item.html", {
        "form": form,
        "titulo": config["titulo_editar"],
        "submit": config["submit_editar"],
    })


@staff_member_required
def eliminar_item(request, model, pk):
    config = get_item_config(model)

    if config is None:
        messages.error(request, "Tipo de ítem inválido.")
        return redirect("listar_catalogo")

    obj = get_object_or_404(config["model_class"], pk=pk)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Ítem eliminado correctamente.")
        return redirect("listar_catalogo")

    return render(request, "catalogo/confirmar_eliminar.html", {
        "obj": obj,
        "model": model,
    })


@login_required
def solicitar_turno(request, servicio_pk):
    servicio = get_object_or_404(Servicio, pk=servicio_pk, activo=True)

    if request.method == "POST":
        form = TurnoForm(request.POST)

        if form.is_valid():
            turno = form.save(commit=False)
            turno.usuario = request.user
            turno.servicio = servicio
            turno.save()

            messages.success(request, "Turno solicitado correctamente.")
            return redirect("mis_turnos")
    else:
        form = TurnoForm()

    return render(request, "turnos/nuevo_turno.html", {
        "form": form,
        "servicio": servicio,
    })


@login_required
def mis_turnos(request):
    turnos = (
        Turno.objects
        .select_related("servicio", "servicio__categoria")
        .filter(usuario=request.user)
        .order_by("-fecha", "-hora")
    )

    return render(request, "turnos/mis_turnos.html", {
        "turnos": turnos,
    })
