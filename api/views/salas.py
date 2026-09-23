from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from app.models import DisponibilidadTurno, Sala
from api.filters import DisponibilidadTurnoFilter
from api.permissions import IsStaffUser
from api.serializers import DisponibilidadTurnoSerializer, SalaSerializer


class SalaViewSet(viewsets.ModelViewSet):
    serializer_class = SalaSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "created_at"]
    ordering = ["nombre"]
    queryset = Sala.objects.all()


class DisponibilidadTurnoViewSet(viewsets.ModelViewSet):
    serializer_class = DisponibilidadTurnoSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DisponibilidadTurnoFilter
    search_fields = ["servicio__nombre", "sala__nombre"]
    ordering_fields = ["servicio__nombre", "sala__nombre", "dia_semana", "hora_inicio"]
    ordering = ["servicio__nombre", "sala__nombre", "dia_semana", "hora_inicio"]
    queryset = DisponibilidadTurno.objects.select_related("servicio", "sala")
