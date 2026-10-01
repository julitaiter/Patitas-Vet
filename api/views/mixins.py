from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response


class ProtectedDestroyMixin:
    """Convierte referencias protegidas del dominio en una respuesta REST 409."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "No se puede eliminar el recurso porque está siendo utilizado. "
                        "Podés desactivarlo en su lugar."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
