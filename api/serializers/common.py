from rest_framework import serializers

from .auth import CurrentUserSerializer


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    usuario = CurrentUserSerializer(read_only=True)


class ApiRootSerializer(serializers.Serializer):
    version = serializers.CharField(read_only=True)
    auth_login = serializers.URLField(read_only=True)
    auth_registro = serializers.URLField(read_only=True)
    me = serializers.URLField(read_only=True)
    categorias = serializers.URLField(read_only=True)
    productos = serializers.URLField(read_only=True)
    servicios = serializers.URLField(read_only=True)
    salas = serializers.URLField(read_only=True)
    disponibilidades = serializers.URLField(read_only=True)
    turnos = serializers.URLField(read_only=True)
    consultas = serializers.URLField(read_only=True)
    buscar = serializers.URLField(read_only=True)
    schema = serializers.URLField(read_only=True)
    docs = serializers.URLField(read_only=True)


class ResultadoBusquedaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    tipo = serializers.ChoiceField(choices=["producto", "servicio"], read_only=True)
    nombre = serializers.CharField(read_only=True)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    imagen_url = serializers.URLField(read_only=True, allow_null=True)
    url = serializers.URLField(read_only=True, allow_null=True)


class BusquedaCatalogoResponseSerializer(serializers.Serializer):
    query = serializers.CharField(read_only=True)
    results = ResultadoBusquedaSerializer(many=True, read_only=True)


class HorariosResponseSerializer(serializers.Serializer):
    servicio = serializers.IntegerField(read_only=True)
    fecha = serializers.DateField(read_only=True)
    horarios = serializers.ListField(
        child=serializers.TimeField(format="%H:%M"),
        read_only=True,
    )
