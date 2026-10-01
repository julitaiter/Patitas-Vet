from rest_framework import serializers

from contacto.models import Consulta, Respuesta


class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ["id", "consulta", "mensaje", "fecha"]
        read_only_fields = ["id", "fecha"]


class ConsultaSerializer(serializers.ModelSerializer):
    respuestas = RespuestaSerializer(many=True, read_only=True)

    class Meta:
        model = Consulta
        fields = [
            "id",
            "nombre",
            "email",
            "telefono",
            "mensaje",
            "estado",
            "fecha",
            "respuestas",
        ]
        read_only_fields = ["id", "fecha", "respuestas"]


class ConsultaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ["id", "nombre", "email", "telefono", "mensaje", "fecha"]
        read_only_fields = ["id", "fecha"]
