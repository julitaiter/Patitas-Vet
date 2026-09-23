from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffUser(BasePermission):
    """Permite acceso unicamente a usuarios autenticados con is_staff=True."""

    message = "Se requieren permisos de staff."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStaffOrReadOnly(BasePermission):
    """Lectura publica y escritura solo para staff."""

    message = "Se requieren permisos de staff para modificar este recurso."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    """Permite acceder al objeto si pertenece al usuario o si el usuario es staff."""

    message = "No tenes permisos para acceder a este recurso."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return getattr(obj, "usuario_id", None) == request.user.id
