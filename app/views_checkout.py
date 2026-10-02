import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import OperationalError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms_checkout import CheckoutForm
from .models import Pedido
from .services.pedidos import PedidoError, crear_pedido, obtener_configuracion_checkout, obtener_cuenta_transferencia


def _draft_key(user):
    return f"checkout_draft_user_{user.pk}"


@login_required
def checkout(request):
    configuracion = obtener_configuracion_checkout()
    cuenta = obtener_cuenta_transferencia()
    codigo = request.GET.get("pedido")
    if codigo and request.method == "GET":
        pedido = get_object_or_404(Pedido.objects.prefetch_related("items"), codigo=codigo, usuario=request.user)
        limpiar_carrito = request.session.pop("checkout_completed_code", None) == pedido.codigo
        return render(request, "carrito/checkout.html", {"pedido": pedido, "limpiar_carrito": limpiar_carrito})

    if request.method == "POST" and request.POST.get("action") == "save_draft":
        campos = set(CheckoutForm.base_fields) - {"comprobante", "cart_payload"}
        borrador = {nombre: request.POST.get(nombre, "") for nombre in campos}
        cache.set(_draft_key(request.user), borrador, timeout=settings.CHECKOUT_DRAFT_TTL)
        return JsonResponse({"ok": True})

    if request.method == "POST":
        form = CheckoutForm(request.POST, request.FILES, configuracion=configuracion, cuenta=cuenta)
        if form.is_valid():
            try:
                carrito = json.loads(form.cleaned_data["cart_payload"])
                pedido = crear_pedido(usuario=request.user, datos=form.cleaned_data, carrito=carrito, configuracion=configuracion)
            except OperationalError:
                form.add_error(None, "No se pudo reservar el stock en este momento. Intentá nuevamente.")
            except (ValueError, TypeError, PedidoError) as exc:
                form.add_error(None, str(exc) if not isinstance(exc, json.JSONDecodeError) else "El carrito contiene datos inválidos.")
            else:
                cache.delete(_draft_key(request.user))
                request.session["checkout_completed_code"] = pedido.codigo
                return redirect(f"/checkout/?pedido={pedido.codigo}")
    else:
        borrador = cache.get(_draft_key(request.user)) or {}
        inicial = {
            "comprador_nombre": request.user.first_name,
            "comprador_apellido": request.user.last_name,
            "comprador_email": request.user.email,
            "tipo_factura": "B", "facturacion_mismos_datos": True,
            "receptor_mismos_datos": True,
        }
        inicial.update(borrador)
        form = CheckoutForm(initial=inicial, configuracion=configuracion, cuenta=cuenta)
    return render(request, "carrito/checkout.html", {
        "form": form, "configuracion": configuracion, "cuenta": cuenta,
        "retiro_disponible": bool(configuracion.nombre_tienda and configuracion.direccion_tienda),
    })


@login_required
def mis_pedidos(request):
    pedidos = (Pedido.objects.filter(usuario=request.user)
               .prefetch_related("items")
               .order_by("-created_at", "-pk"))
    pagina = Paginator(pedidos, 8).get_page(request.GET.get("page"))
    return render(request, "pedidos/mis_pedidos.html", {"pagina": pagina})


@login_required
def detalle_pedido(request, codigo):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("items"),
        codigo=codigo, usuario=request.user,
    )
    return render(request, "pedidos/detalle_pedido.html", {"pedido": pedido})
