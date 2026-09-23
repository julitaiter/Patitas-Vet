from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import Turno
from api.filters import TurnoFilter
from api.permissions import IsStaffUser
from api.serializers import TurnoCreateSerializer, TurnoReadSerializer, TurnoStaffUpdateSerializer


class TurnoViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TurnoFilter
    search_fields = ["mascota", "servicio__nombre", "sala__nombre", "usuario__username", "usuario__email"]
    ordering_fields = ["fecha", "hora", "created_at", "estado"]
    ordering = ["fecha", "hora"]

    def get_queryset(self):
        qs = Turno.objects.select_related("usuario", "servicio", "sala", "servicio__categoria")
        if self.request.user.is_staff:
            return qs
        return qs.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return TurnoCreateSerializer
        if self.action in {"update", "partial_update"}:
            return TurnoStaffUpdateSerializer
        return TurnoReadSerializer

    def get_permissions(self):
        if self.action in {"update", "partial_update", "confirmar", "realizar", "pendiente"}:
            return [IsStaffUser()]
        return [IsAuthenticated()]

    def _estado_response(self, turno):
        return Response(TurnoReadSerializer(turno, context={"request": self.request}).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        turno = self.get_object()
        if turno.estado == Turno.ESTADO_REALIZADO:
            return Response(
                {"detail": "Un turno realizado no puede cancelarse."},
                status=status.HTTP_409_CONFLICT,
            )
        if turno.estado != Turno.ESTADO_CANCELADO:
            turno.estado = Turno.ESTADO_CANCELADO
            turno.save(update_fields=["estado", "updated_at"])
        return self._estado_response(turno)

    @action(detail=True, methods=["post"], permission_classes=[IsStaffUser])
    def confirmar(self, request, pk=None):
        turno = self.get_object()
        turno.estado = Turno.ESTADO_CONFIRMADO
        turno.save(update_fields=["estado", "updated_at"])
        return self._estado_response(turno)

    @action(detail=True, methods=["post"], permission_classes=[IsStaffUser])
    def realizar(self, request, pk=None):
        turno = self.get_object()
        turno.estado = Turno.ESTADO_REALIZADO
        turno.save(update_fields=["estado", "updated_at"])
        return self._estado_response(turno)

    @action(detail=True, methods=["post"], permission_classes=[IsStaffUser])
    def pendiente(self, request, pk=None):
        turno = self.get_object()
        turno.estado = Turno.ESTADO_PENDIENTE
        turno.save(update_fields=["estado", "updated_at"])
        return self._estado_response(turno)
