from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.models import Producto, Servicio
from api.serializers import (
    BusquedaCatalogoResponseSerializer,
    ProductoListSerializer,
    ServicioListSerializer,
)


class BuscarCatalogoView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = BusquedaCatalogoResponseSerializer

    @extend_schema(
        parameters=[OpenApiParameter("q", str, description="Texto de búsqueda (mínimo 2 caracteres).")],
        responses=BusquedaCatalogoResponseSerializer,
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response({"query": query, "results": []})

        productos = (
            Producto.objects.select_related("categoria")
            .filter(activo=True, categoria__activa=True)
            .filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))[:10]
        )
        servicios = (
            Servicio.objects.select_related("categoria")
            .filter(activo=True, categoria__activa=True)
            .filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))[:10]
        )

        resultados = []
        for item in ProductoListSerializer(productos, many=True, context={"request": request}).data:
            resultados.append(
                {
                    "id": item["id"],
                    "tipo": "producto",
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "imagen_url": item["imagen_url"],
                    "url": item["detalle_url"],
                }
            )
        for item in ServicioListSerializer(servicios, many=True, context={"request": request}).data:
            resultados.append(
                {
                    "id": item["id"],
                    "tipo": "servicio",
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "imagen_url": item["imagen_url"],
                    "url": item["detalle_url"],
                }
            )

        resultados.sort(key=lambda item: item["nombre"].lower())
        return Response({"query": query, "results": resultados[:12]})
