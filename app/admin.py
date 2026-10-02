from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .forms import AjustarStockForm
from .models import (
    Categoria,
    DisponibilidadTurno,
    Producto,
    Sala,
    Servicio,
    Turno,
    Pedido, PedidoItem, ComprobanteTransferencia, CuentaTransferencia,
    ConfiguracionCheckout, HistorialEstadoPedido,
    PreguntaFrecuente,
)
from .services.pedidos import PedidoError, cambiar_estado_pedido


class BasicAdminMixin:
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PreguntaFrecuente)
class PreguntaFrecuenteAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = ["pregunta", "activo", "orden", "updated_at"]
    list_filter = ["activo"]
    search_fields = ["pregunta", "descripcion", "contenido"]
    list_editable = ["activo", "orden"]
    ordering = ["orden", "pregunta"]


class CatalogoAdminMixin(BasicAdminMixin):
    readonly_fields = ["created_at", "updated_at", "imagen_preview"]

    list_filter = ["categoria", "activo", "destacado"]
    search_fields = ["nombre", "descripcion", "categoria__nombre"]
    list_select_related = ["categoria"]
    ordering = ["nombre"]

    actions = [
        "activar_items",
        "desactivar_items",
        "marcar_destacados",
        "quitar_destacados",
    ]

    fieldsets = (
        (
            "Datos principales",
            {
                "fields": (
                    "nombre",
                    "descripcion",
                    "categoria",
                    "precio",
                )
            },
        ),
        (
            "Imagen",
            {
                "fields": (
                    "imagen",
                    "imagen_preview",
                )
            },
        ),
        (
            "Visibilidad",
            {
                "fields": (
                    "activo",
                    "destacado",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.display(description="Imagen")
    def imagen_preview(self, obj):
        if obj and obj.imagen:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;" />',
                obj.imagen.url,
            )

        return "-"

    @admin.display(description="Activo", boolean=True, ordering="activo")
    def activo_icono(self, obj):
        return obj.activo

    @admin.display(description="Destacado", boolean=True, ordering="destacado")
    def destacado_icono(self, obj):
        return obj.destacado

    @admin.action(description="Activar seleccionados")
    def activar_items(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activo=False)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ningún ítem. Los seleccionados ya estaban activos.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activo=True, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} ítem(s) activado(s) correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Desactivar seleccionados")
    def desactivar_items(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activo=True)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ningún ítem. Los seleccionados ya estaban inactivos.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activo=False, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} ítem(s) desactivado(s) correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Marcar como destacados")
    def marcar_destacados(self, request, queryset):
        queryset_a_actualizar = queryset.filter(destacado=False)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ningún ítem. Los seleccionados ya estaban destacados.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(destacado=True, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} ítem(s) marcado(s) como destacado(s).",
            level=messages.SUCCESS,
        )

    @admin.action(description="Quitar de destacados")
    def quitar_destacados(self, request, queryset):
        queryset_a_actualizar = queryset.filter(destacado=True)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ningún ítem. Los seleccionados no estaban destacados.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(
            destacado=False, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} ítem(s) quitado(s) de destacados.",
            level=messages.SUCCESS,
        )


@admin.register(Categoria)
class CategoriaAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = [
        "nombre",
        "activa",
        "created_at",
    ]

    list_filter = [
        "activa",
    ]

    search_fields = [
        "nombre",
    ]

    list_editable = [
        "activa",
    ]

    ordering = [
        "nombre",
    ]

    actions = [
        "activar_categorias",
        "desactivar_categorias",
    ]

    fieldsets = (
        (
            "Datos de la categoría",
            {
                "fields": (
                    "nombre",
                    "activa",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.action(description="Activar categorías seleccionadas")
    def activar_categorias(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=False)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna categoría. Las seleccionadas ya estaban activas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=True, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} categoría(s) activada(s) correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Desactivar categorías seleccionadas")
    def desactivar_categorias(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=True)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna categoría. Las seleccionadas ya estaban inactivas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=False, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} categoría(s) desactivada(s) correctamente.",
            level=messages.SUCCESS,
        )


@admin.register(Sala)
class SalaAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = [
        "nombre",
        "activa",
        "created_at",
    ]

    list_filter = [
        "activa",
    ]

    search_fields = [
        "nombre",
        "descripcion",
    ]

    list_editable = [
        "activa",
    ]

    ordering = [
        "nombre",
    ]

    actions = [
        "activar_salas",
        "desactivar_salas",
    ]

    fieldsets = (
        (
            "Datos de la sala",
            {
                "fields": (
                    "nombre",
                    "descripcion",
                    "activa",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.action(description="Activar salas seleccionadas")
    def activar_salas(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=False)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna sala. Las seleccionadas ya estaban activas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=True, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} sala(s) activada(s) correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Desactivar salas seleccionadas")
    def desactivar_salas(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=True)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna sala. Las seleccionadas ya estaban inactivas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=False, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} sala(s) desactivada(s) correctamente.",
            level=messages.SUCCESS,
        )


@admin.register(DisponibilidadTurno)
class DisponibilidadTurnoAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = [
        "servicio",
        "sala",
        "dia_semana",
        "hora_inicio",
        "hora_fin",
        "intervalo_minutos",
        "activa",
    ]

    list_filter = [
        "servicio",
        "sala",
        "dia_semana",
        "activa",
    ]

    search_fields = [
        "servicio__nombre",
        "sala__nombre",
    ]

    list_select_related = [
        "servicio",
        "sala",
    ]

    list_editable = [
        "activa",
    ]

    ordering = [
        "servicio",
        "sala",
        "dia_semana",
        "hora_inicio",
    ]

    actions = [
        "activar_disponibilidades",
        "desactivar_disponibilidades",
    ]

    fieldsets = (
        (
            "Servicio y sala",
            {
                "fields": (
                    "servicio",
                    "sala",
                    "activa",
                )
            },
        ),
        (
            "Día y horario",
            {
                "fields": (
                    "dia_semana",
                    "hora_inicio",
                    "hora_fin",
                    "intervalo_minutos",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.action(description="Activar disponibilidades seleccionadas")
    def activar_disponibilidades(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=False)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna disponibilidad. Las seleccionadas ya estaban activas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=True, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} disponibilidad(es) activada(s) correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Desactivar disponibilidades seleccionadas")
    def desactivar_disponibilidades(self, request, queryset):
        queryset_a_actualizar = queryset.filter(activa=True)
        total = queryset_a_actualizar.count()

        if total == 0:
            self.message_user(
                request,
                "No se modificó ninguna disponibilidad. Las seleccionadas ya estaban inactivas.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(activa=False, updated_at=timezone.now())

        self.message_user(
            request,
            f"{total} disponibilidad(es) desactivada(s) correctamente.",
            level=messages.SUCCESS,
        )


@admin.register(Servicio)
class ServicioAdmin(CatalogoAdminMixin, admin.ModelAdmin):
    list_display = [
        "imagen_preview",
        "nombre",
        "categoria",
        "precio",
        "duracion_minutos",
        "activo_icono",
        "destacado_icono",
    ]

    list_filter = [
        "categoria",
        "activo",
        "destacado",
    ]

    search_fields = [
        "nombre",
        "descripcion",
        "categoria__nombre",
    ]

    list_select_related = [
        "categoria",
    ]

    list_editable = [
        "precio",
        "duracion_minutos",
    ]

    fieldsets = (
        (
            "Datos principales",
            {
                "fields": (
                    "nombre",
                    "descripcion",
                    "categoria",
                    "precio",
                    "duracion_minutos",
                )
            },
        ),
        (
            "Imagen",
            {
                "fields": (
                    "imagen",
                    "imagen_preview",
                )
            },
        ),
        (
            "Visibilidad",
            {
                "fields": (
                    "activo",
                    "destacado",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )


@admin.register(Producto)
class ProductoAdmin(CatalogoAdminMixin, admin.ModelAdmin):
    list_display = [
        "imagen_preview",
        "nombre",
        "categoria",
        "precio",
        "stock_badge",
        "activo_icono",
        "destacado_icono",
    ]

    list_editable = [
        "precio",
    ]

    actions = CatalogoAdminMixin.actions + ["ajustar_stock"]

    fieldsets = (
        (
            "Datos principales",
            {
                "fields": (
                    "nombre",
                    "descripcion",
                    "categoria",
                    "precio",
                    "stock",
                )
            },
        ),
        (
            "Imagen",
            {
                "fields": (
                    "imagen",
                    "imagen_preview",
                )
            },
        ),
        (
            "Visibilidad",
            {
                "fields": (
                    "activo",
                    "destacado",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.display(description="Stock", ordering="stock")
    def stock_badge(self, obj):
        if obj.stock <= 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;">Sin stock</span>'
            )

        if obj.stock <= 5:
            return format_html(
                '<span style="background-color: #ffc107; color: #212529; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;">Stock bajo: {}</span>',
                obj.stock,
            )

        return format_html(
            '<span style="background-color: #198754; color: white; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;">{}</span>',
            obj.stock,
        )

    @admin.action(description="Ajustar stock de los productos seleccionados", permissions=["change"])
    def ajustar_stock(self, request, queryset):
        if "aplicar" in request.POST:
            form = AjustarStockForm(request.POST)
            if form.is_valid():
                operacion = form.cleaned_data["operacion"]
                cantidad = form.cleaned_data["cantidad"]

                with transaction.atomic():
                    for producto in queryset.select_for_update():
                        if operacion == AjustarStockForm.OPERACION_ESTABLECER:
                            producto.stock = cantidad
                        elif operacion == AjustarStockForm.OPERACION_SUMAR:
                            producto.stock += cantidad
                        else:
                            producto.stock = max(0, producto.stock - cantidad)
                        producto.save(update_fields=["stock", "updated_at"])

                self.message_user(
                    request,
                    f"Stock actualizado en {queryset.count()} producto(s).",
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect(reverse("admin:app_producto_changelist"))
        else:
            form = AjustarStockForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Ajustar stock",
            "form": form,
            "productos": queryset,
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        }
        return TemplateResponse(
            request,
            "admin/app/producto/ajustar_stock.html",
            context,
        )


@admin.register(Turno)
class TurnoAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = [
        "servicio",
        "sala",
        "usuario",
        "mascota",
        "fecha",
        "hora",
        "estado_badge",
    ]

    list_filter = [
        "estado",
        "fecha",
        "servicio",
        "sala",
    ]

    search_fields = [
        "usuario__username",
        "usuario__email",
        "mascota",
        "servicio__nombre",
        "sala__nombre",
    ]

    list_select_related = [
        "servicio",
        "sala",
        "usuario",
    ]

    date_hierarchy = "fecha"

    ordering = [
        "fecha",
        "hora",
    ]

    actions = [
        "confirmar_turno",
        "cancelar_turno",
        "realizar_turno",
        "marcar_turno_pendiente",
    ]

    fieldsets = (
        (
            "Datos del turno",
            {
                "fields": (
                    "usuario",
                    "servicio",
                    "sala",
                    "mascota",
                    "estado",
                )
            },
        ),
        (
            "Fecha y horario",
            {
                "fields": (
                    "fecha",
                    "hora",
                )
            },
        ),
        (
            "Observaciones",
            {
                "fields": (
                    "observaciones",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.display(description="Estado", ordering="estado")
    def estado_badge(self, obj):
        colores = {
            Turno.ESTADO_PENDIENTE: {
                "bg": "#ffc107",
                "text": "#212529",
            },
            Turno.ESTADO_CONFIRMADO: {
                "bg": "#198754",
                "text": "#ffffff",
            },
            Turno.ESTADO_CANCELADO: {
                "bg": "#dc3545",
                "text": "#ffffff",
            },
            Turno.ESTADO_REALIZADO: {
                "bg": "#6c757d",
                "text": "#ffffff",
            },
        }

        color = colores.get(
            obj.estado,
            {
                "bg": "#6c757d",
                "text": "#ffffff",
            },
        )

        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;">{}</span>',
            color["bg"],
            color["text"],
            obj.get_estado_display(),
        )

    def cambiar_estado_queryset(self, request, queryset, nuevo_estado, etiqueta_estado):
        total_seleccionados = queryset.count()

        if total_seleccionados == 0:
            self.message_user(
                request,
                "No se seleccionó ningún turno.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar = queryset.exclude(estado=nuevo_estado)
        total_a_actualizar = queryset_a_actualizar.count()

        if total_a_actualizar == 0:
            self.message_user(
                request,
                f"No se modificó ningún turno. Los {total_seleccionados} turno(s) seleccionado(s) ya estaban en estado {etiqueta_estado}.",
                level=messages.WARNING,
            )
            return

        queryset_a_actualizar.update(
            estado=nuevo_estado,
            updated_at=timezone.now(),
        )

        total_sin_cambios = total_seleccionados - total_a_actualizar

        if total_sin_cambios:
            self.message_user(
                request,
                f"{total_a_actualizar} turno(s) marcado(s) como {etiqueta_estado}. {total_sin_cambios} ya estaban en ese estado.",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                f"{total_a_actualizar} turno(s) marcado(s) como {etiqueta_estado}.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Confirmar turnos seleccionados")
    def confirmar_turno(self, request, queryset):
        self.cambiar_estado_queryset(
            request=request,
            queryset=queryset,
            nuevo_estado=Turno.ESTADO_CONFIRMADO,
            etiqueta_estado="confirmado",
        )

    @admin.action(description="Cancelar turnos seleccionados")
    def cancelar_turno(self, request, queryset):
        self.cambiar_estado_queryset(
            request=request,
            queryset=queryset,
            nuevo_estado=Turno.ESTADO_CANCELADO,
            etiqueta_estado="cancelado",
        )

    @admin.action(description="Marcar como realizados")
    def realizar_turno(self, request, queryset):
        self.cambiar_estado_queryset(
            request=request,
            queryset=queryset,
            nuevo_estado=Turno.ESTADO_REALIZADO,
            etiqueta_estado="realizado",
        )

    @admin.action(description="Marcar como pendientes")
    def marcar_turno_pendiente(self, request, queryset):
        self.cambiar_estado_queryset(
            request=request,
            queryset=queryset,
            nuevo_estado=Turno.ESTADO_PENDIENTE,
            etiqueta_estado="pendiente",
        )


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    can_delete = False
    readonly_fields = ["producto", "producto_nombre", "precio_unitario", "cantidad", "subtotal"]

    def has_add_permission(self, request, obj=None):
        return False


class ComprobanteInline(admin.StackedInline):
    model = ComprobanteTransferencia
    extra = 0
    can_delete = False
    readonly_fields = ["archivo", "nombre_original", "content_type", "tamanio", "created_at", "updated_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "usuario", "estado", "estado_pago", "tipo_entrega", "medio_pago", "total", "created_at"]
    list_filter = ["estado", "estado_pago", "tipo_entrega", "medio_pago", "tipo_factura", "created_at"]
    search_fields = ["codigo", "usuario__username", "comprador_nombre", "comprador_apellido", "comprador_email", "comprador_dni"]
    inlines = [PedidoItemInline, ComprobanteInline]
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in Pedido._meta.fields if f.name not in ("estado", "estado_pago")]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        anterior = Pedido.objects.get(pk=obj.pk)
        if obj.estado != anterior.estado:
            try:
                cambiar_estado_pedido(anterior, obj.estado, request.user)
            except PedidoError as exc:
                self.message_user(request, str(exc), level=messages.ERROR)
        if obj.estado_pago != anterior.estado_pago:
            Pedido.objects.filter(pk=obj.pk).update(estado_pago=obj.estado_pago)


@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ["pedido", "producto_nombre", "cantidad", "precio_unitario", "subtotal"]
    readonly_fields = ["pedido", "producto", "producto_nombre", "precio_unitario", "cantidad", "subtotal"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ComprobanteTransferencia)
class ComprobanteTransferenciaAdmin(admin.ModelAdmin):
    list_display = ["pedido", "nombre_original", "content_type", "tamanio", "created_at"]
    readonly_fields = ["pedido", "archivo", "nombre_original", "content_type", "tamanio", "created_at", "updated_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CuentaTransferencia)
class CuentaTransferenciaAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = ["banco", "titular", "alias", "activa", "principal"]
    list_filter = ["activa", "principal"]
    search_fields = ["banco", "titular", "alias", "cbu_cvu"]


@admin.register(ConfiguracionCheckout)
class ConfiguracionCheckoutAdmin(BasicAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Envío", {"fields": ("costo_envio", "envio_gratis_desde"),
                   "description": "El mínimo para envío gratis se calcula sobre el subtotal. Dejalo vacío para cobrar siempre el envío a domicilio."}),
        ("Retiro por tienda", {"fields": ("nombre_tienda", "direccion_tienda", "indicaciones_retiro")}),
        ("Notificaciones y comprobantes", {"fields": ("email_negocio", "comprobante_max_mb")}),
        ("Fechas", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return not ConfiguracionCheckout.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ["pedido", "estado_anterior", "estado_nuevo", "usuario", "fecha"]
    readonly_fields = ["pedido", "estado_anterior", "estado_nuevo", "usuario", "fecha", "observacion"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
