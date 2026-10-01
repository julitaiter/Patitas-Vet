from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny

from api.permissions import IsStaffUser
from api.serializers import (
    ConsultaCreateSerializer,
    ConsultaSerializer,
    RespuestaSerializer,
)
from contacto.models import Consulta, Respuesta


class ConsultaViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "email", "telefono", "mensaje"]
    ordering_fields = ["fecha", "estado", "nombre"]
    ordering = ["-fecha"]

    def get_queryset(self):
        return Consulta.objects.prefetch_related("respuestas")

    def get_serializer_class(self):
        if self.action == "create":
            return ConsultaCreateSerializer
        return ConsultaSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsStaffUser()]


class RespuestaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RespuestaSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["consulta__nombre", "consulta__email", "mensaje"]
    ordering_fields = ["fecha"]
    ordering = ["-fecha"]
    queryset = Respuesta.objects.select_related("consulta")
