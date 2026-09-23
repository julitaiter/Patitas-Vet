from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Producto, Servicio
from api.serializers import ProductoListSerializer, ServicioListSerializer


class BuscarCatalogoView(APIView):
    permission_classes = [AllowAny]

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
