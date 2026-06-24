from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import Categoria, Producto, Servicio, Turno


class BasicAdminMixin:
    readonly_fields = ["created_at", "updated_at"]

    def actualizar_queryset(self, request, queryset, campos, mensaje_ok, mensaje_sin_cambios=None):
        total = queryset.count()

        if total == 0:
            self.message_user(
                request,
                "No se seleccionó ningún elemento.",
                level=messages.WARNING,
            )
            return

        campos["updated_at"] = timezone.now()
        actualizados = queryset.update(**campos)

        if actualizados:
            self.message_user(
                request,
                mensaje_ok.format(total=actualizados),
                level=messages.SUCCESS,
            )
        elif mensaje_sin_cambios:
            self.message_user(
                request,
                mensaje_sin_cambios,
                level=messages.WARNING,
            )


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

    @admin.display(description="Precio", ordering="precio")
    def precio_formateado(self, obj):
        return f"$ {obj.precio}"

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


@admin.register(Turno)
class TurnoAdmin(BasicAdminMixin, admin.ModelAdmin):
    list_display = [
        "servicio",
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
    ]

    search_fields = [
        "usuario__username",
        "usuario__email",
        "mascota",
        "servicio__nombre",
    ]

    list_select_related = [
        "servicio",
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
