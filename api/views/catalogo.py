from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import Categoria, Producto, Servicio
from app.services.turnos import obtener_horarios_disponibles
from api.filters import ProductoFilter, ServicioFilter
from api.permissions import IsStaffOrReadOnly
from api.serializers import (
    CategoriaSerializer,
    ProductoDetailSerializer,
    ProductoListSerializer,
    ServicioDetailSerializer,
    ServicioListSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "created_at"]
    ordering = ["nombre"]

    def get_queryset(self):
        qs = Categoria.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(activa=True)
        return qs


class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter
    search_fields = ["nombre", "descripcion", "categoria__nombre"]
    ordering_fields = ["nombre", "precio", "stock", "created_at"]
    ordering = ["nombre"]

    def get_queryset(self):
        qs = Producto.objects.select_related("categoria")
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(activo=True, categoria__activa=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProductoListSerializer
        return ProductoDetailSerializer

    @action(detail=True, methods=["get"], permission_classes=[])
    def stock(self, request, pk=None):
        producto = self.get_object()
        try:
            cantidad = int(request.query_params.get("cantidad", 1))
        except (TypeError, ValueError):
            return Response(
                {"ok": False, "mensaje": "La cantidad debe ser un entero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cantidad <= 0:
            return Response(
                {"ok": False, "mensaje": "La cantidad debe ser mayor a cero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        disponible = producto.activo and producto.stock >= cantidad
        serializer = ProductoDetailSerializer(producto, context={"request": request})
        return Response(
            {
                "ok": disponible,
                "mensaje": "Producto disponible." if disponible else "Stock insuficiente.",
                "cantidad_solicitada": cantidad,
                "stock": producto.stock,
                "producto": serializer.data,
            },
            status=status.HTTP_200_OK if disponible else status.HTTP_409_CONFLICT,
        )


class ServicioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServicioFilter
    search_fields = ["nombre", "descripcion", "categoria__nombre"]
    ordering_fields = ["nombre", "precio", "duracion_minutos", "created_at"]
    ordering = ["nombre"]

    def get_queryset(self):
        qs = Servicio.objects.select_related("categoria")
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(activo=True, categoria__activa=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ServicioListSerializer
        return ServicioDetailSerializer

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def horarios(self, request, pk=None):
        servicio = self.get_object()
        fecha_raw = request.query_params.get("fecha", "")
        try:
            fecha = date.fromisoformat(fecha_raw)
        except ValueError:
            return Response(
                {"detail": "El parametro fecha debe usar formato YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        horarios = obtener_horarios_disponibles(servicio, fecha)
        return Response(
            {
                "servicio": servicio.pk,
                "fecha": fecha.isoformat(),
                "horarios": [hora.strftime("%H:%M") for hora in horarios],
            }
        )
