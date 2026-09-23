from rest_framework import serializers

from app.models import Categoria, Producto, Servicio
from api.utils import build_absolute_detail_url


class CategoriaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "activa", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ItemCatalogoMixin(serializers.ModelSerializer):
    categoria_detalle = CategoriaResumenSerializer(source="categoria", read_only=True)
    imagen_url = serializers.SerializerMethodField()
    detalle_url = serializers.SerializerMethodField()

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get("request")
        url = obj.imagen.url
        return request.build_absolute_uri(url) if request else url

    def get_detalle_url(self, obj):
        raise NotImplementedError


class ProductoListSerializer(ItemCatalogoMixin):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "precio",
            "stock",
            "categoria",
            "categoria_detalle",
            "imagen_url",
            "destacado",
            "detalle_url",
        ]
        read_only_fields = ["id"]

    def get_detalle_url(self, obj):
        return build_absolute_detail_url(self.context.get("request"), "detalle_producto", obj.pk)


class ProductoDetailSerializer(ItemCatalogoMixin):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "imagen",
            "imagen_url",
            "categoria",
            "categoria_detalle",
            "activo",
            "destacado",
            "detalle_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "imagen_url", "detalle_url", "created_at", "updated_at"]

    def get_detalle_url(self, obj):
        return build_absolute_detail_url(self.context.get("request"), "detalle_producto", obj.pk)


class ServicioListSerializer(ItemCatalogoMixin):
    class Meta:
        model = Servicio
        fields = [
            "id",
            "nombre",
            "precio",
            "duracion_minutos",
            "categoria",
            "categoria_detalle",
            "imagen_url",
            "destacado",
            "detalle_url",
        ]
        read_only_fields = ["id"]

    def get_detalle_url(self, obj):
        return build_absolute_detail_url(self.context.get("request"), "detalle_servicio", obj.pk)


class ServicioDetailSerializer(ItemCatalogoMixin):
    class Meta:
        model = Servicio
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "duracion_minutos",
            "imagen",
            "imagen_url",
            "categoria",
            "categoria_detalle",
            "activo",
            "destacado",
            "detalle_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "imagen_url", "detalle_url", "created_at", "updated_at"]

    def get_detalle_url(self, obj):
        return build_absolute_detail_url(self.context.get("request"), "detalle_servicio", obj.pk)
