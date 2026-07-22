from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import (
    PerfilForm,
    ProductoForm,
    ServicioForm,
    TurnoEmpleadoForm,
    TurnoForm,
)
from .models import Categoria, Producto, Sala, Servicio, Turno
from .services.turnos import obtener_horarios_disponibles


def index(request):
    servicios_destacados = (
        Servicio.objects
        .select_related("categoria", "sala")
        .filter(activo=True, destacado=True)
        .order_by("nombre")[:3]
    )

    if not servicios_destacados:
        servicios_destacados = (
            Servicio.objects
            .select_related("categoria", "sala")
            .filter(activo=True)
            .order_by("nombre")[:3]
        )

    return render(request, "index.html", {
        "servicios_destacados": servicios_destacados,
    })


@login_required
def mi_perfil(request):
    turnos_recientes = (
        Turno.objects
        .select_related("servicio", "sala")
        .filter(usuario=request.user)
        .order_by("-fecha", "-hora")[:3]
    )

    return render(request, "account/mi_perfil.html", {
        "turnos_recientes": turnos_recientes,
    })


@login_required
def editar_perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("mi_perfil")
    else:
        form = PerfilForm(instance=request.user)

    return render(request, "account/editar_perfil.html", {
        "form": form,
    })


def listar_catalogo(request):
    query = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    categoria_id_int = int(categoria_id) if categoria_id.isdigit() else None

    servicios = Servicio.objects.select_related(
        "categoria", "sala").filter(activo=True)
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


def detalle_item(request, model, pk):
    config = get_item_config(model)

    if config is None:
        messages.error(request, "Tipo de ítem inválido.")
        return redirect("listar_catalogo")

    queryset = config["model_class"].objects.select_related("categoria")
    if model == "servicio":
        queryset = queryset.select_related("sala")

    item = get_object_or_404(queryset, pk=pk, activo=True)
    return render(request, "catalogo/detalle_item.html", {
        "item": item,
        "model": model,
    })


@login_required
def ver_carrito(request):
    return render(request, "carrito/ver_carrito.html")


@login_required
@require_GET
def validar_stock_producto(request, pk):
    try:
        cantidad = int(request.GET.get("cantidad", 1))
    except (TypeError, ValueError):
        cantidad = 0

    if cantidad < 1:
        return JsonResponse({
            "ok": False,
            "mensaje": "La cantidad solicitada debe ser mayor a cero.",
        }, status=400)

    try:
        producto = Producto.objects.get(pk=pk)
    except Producto.DoesNotExist:
        return JsonResponse({
            "ok": False,
            "mensaje": "El producto no existe.",
        }, status=404)

    if not producto.activo:
        return JsonResponse({
            "ok": False,
            "mensaje": "Este producto ya no está disponible.",
        }, status=404)

    if producto.stock < 1:
        return JsonResponse({
            "ok": False,
            "mensaje": "Este producto no tiene stock disponible.",
        })

    if cantidad > producto.stock:
        return JsonResponse({
            "ok": False,
            "mensaje": f"Solo hay {producto.stock} unidad(es) disponibles.",
        })

    return JsonResponse({
        "ok": True,
        "mensaje": "Producto disponible.",
        "producto": {
            "id": producto.pk,
            "nombre": producto.nombre,
            "precio": str(producto.precio),
            "imagen_url": producto.imagen.url if producto.imagen else "",
            "stock": producto.stock,
            "detalle_url": reverse("detalle_producto", kwargs={"pk": producto.pk}),
        },
    })


@require_GET
def buscar_catalogo_ajax(request):
    term = request.GET.get("term", "").strip()
    if len(term) < 2:
        return JsonResponse([], safe=False)

    filtro = Q(nombre__icontains=term) | Q(descripcion__icontains=term)
    productos = Producto.objects.filter(activo=True).filter(filtro).order_by("nombre")[:6]
    servicios = Servicio.objects.filter(activo=True).filter(filtro).order_by("nombre")[:6]

    resultados = []
    for item, tipo, url_name in (
        *((item, "Producto", "detalle_producto") for item in productos),
        *((item, "Servicio", "detalle_servicio") for item in servicios),
    ):
        resultados.append({
            "label": f"{item.nombre} - {tipo}",
            "value": item.nombre,
            "tipo": tipo,
            "url": reverse(url_name, kwargs={"pk": item.pk}),
            "precio": str(item.precio),
            "imagen_url": item.imagen.url if item.imagen else "",
        })

    resultados.sort(key=lambda resultado: resultado["value"].lower())
    return JsonResponse(resultados[:12], safe=False)


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
    servicio = get_object_or_404(
        Servicio.objects.select_related("sala"),
        pk=servicio_pk,
        activo=True,
    )

    if request.method == "POST":
        form = TurnoForm(request.POST, servicio=servicio)

        if form.is_valid():
            turno = form.save(commit=False)
            turno.usuario = request.user
            turno.servicio = servicio
            turno.sala = servicio.sala
            turno.save()

            messages.success(request, "Turno solicitado correctamente.")
            return redirect("mis_turnos")
    else:
        form = TurnoForm(servicio=servicio)

    return render(request, "turnos/nuevo_turno.html", {
        "form": form,
        "servicio": servicio,
    })


@login_required
def mis_turnos(request):
    turnos = (
        Turno.objects
        .select_related("servicio", "sala", "servicio__categoria")
        .filter(usuario=request.user)
        .order_by("-fecha", "-hora")
    )

    return render(request, "turnos/mis_turnos.html", {
        "turnos": turnos,
    })


@login_required
def horarios_disponibles(request):
    servicio_id = request.GET.get("servicio")
    fecha_str = request.GET.get("fecha")

    if not servicio_id or not fecha_str:
        return JsonResponse({"horarios": []})

    try:
        servicio = Servicio.objects.select_related("sala").get(
            pk=servicio_id,
            activo=True,
        )
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except (Servicio.DoesNotExist, ValueError):
        return JsonResponse({"horarios": []})

    horarios = obtener_horarios_disponibles(servicio.sala, fecha)

    return JsonResponse({
        "horarios": [
            {
                "value": hora.strftime("%H:%M"),
                "label": hora.strftime("%H:%M"),
            }
            for hora in horarios
        ]
    })


@staff_member_required
def gestionar_turnos(request):
    fecha = request.GET.get("fecha", "").strip()
    estado = request.GET.get("estado", "").strip()
    servicio_id = request.GET.get("servicio", "").strip()
    sala_id = request.GET.get("sala", "").strip()
    query = request.GET.get("q", "").strip()

    turnos = Turno.objects.select_related(
        "usuario",
        "servicio",
        "servicio__categoria",
        "sala",
    )

    servicios = Servicio.objects.filter(activo=True).order_by("nombre")
    salas = Sala.objects.filter(activa=True).order_by("nombre")

    if fecha:
        turnos = turnos.filter(fecha=fecha)

    if estado:
        turnos = turnos.filter(estado=estado)

    if servicio_id.isdigit():
        turnos = turnos.filter(servicio_id=int(servicio_id))

    if sala_id.isdigit():
        turnos = turnos.filter(sala_id=int(sala_id))

    if query:
        turnos = turnos.filter(
            Q(usuario__username__icontains=query)
            | Q(usuario__email__icontains=query)
            | Q(mascota__icontains=query)
            | Q(servicio__nombre__icontains=query)
            | Q(sala__nombre__icontains=query)
        )

    turnos = turnos.order_by("fecha", "hora", "sala__nombre")

    return render(request, "turnos/gestionar_turnos.html", {
        "turnos": turnos,
        "servicios": servicios,
        "salas": salas,
        "estados": Turno.ESTADOS,
        "fecha": fecha,
        "estado": estado,
        "servicio_id": int(servicio_id) if servicio_id.isdigit() else None,
        "sala_id": int(sala_id) if sala_id.isdigit() else None,
        "query": query,
    })


@staff_member_required
def editar_turno_empleado(request, pk):
    turno = get_object_or_404(Turno, pk=pk)

    if request.method == "POST":
        form = TurnoEmpleadoForm(request.POST, instance=turno)

        if form.is_valid():
            turno = form.save(commit=False)
            turno.sala = turno.servicio.sala
            turno.save()

            messages.success(request, "Turno actualizado correctamente.")
            return redirect("gestionar_turnos")
    else:
        form = TurnoEmpleadoForm(instance=turno)

    return render(request, "turnos/editar_turno_empleado.html", {
        "form": form,
        "turno": turno,
    })


@staff_member_required
@require_POST
def cambiar_estado_turno(request, pk, estado):
    turno = get_object_or_404(Turno, pk=pk)

    estados_validos = dict(Turno.ESTADOS)

    if estado not in estados_validos:
        messages.error(request, "Estado inválido.")
        return redirect("gestionar_turnos")

    turno.estado = estado
    turno.save(update_fields=["estado", "updated_at"])

    messages.success(
        request, f"Turno marcado como {estados_validos[estado].lower()}.")
    return redirect("gestionar_turnos")
