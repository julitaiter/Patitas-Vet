import random

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from app.models import Servicio, Turno
from app.services.turnos import (
    obtener_sala_disponible_para_turno,
    obtener_salas_disponibles_para_turno,
    turno_esta_disponible,
)


class TurnoReadSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source="servicio.nombre", read_only=True)
    sala_nombre = serializers.CharField(source="sala.nombre", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Turno
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "servicio",
            "servicio_nombre",
            "sala",
            "sala_nombre",
            "fecha",
            "hora",
            "mascota",
            "observaciones",
            "estado",
            "estado_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TurnoCreateSerializer(serializers.ModelSerializer):
    servicio = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.filter(activo=True))

    class Meta:
        model = Turno
        fields = ["servicio", "fecha", "hora", "mascota", "observaciones"]

    def validate(self, attrs):
        fecha = attrs.get("fecha")
        hora = attrs.get("hora")
        servicio = attrs.get("servicio")

        hoy = timezone.localdate()
        if fecha < hoy:
            raise serializers.ValidationError({"fecha": "No se puede reservar una fecha pasada."})
        if fecha == hoy and hora <= timezone.localtime().time():
            raise serializers.ValidationError({"hora": "No se puede reservar un horario pasado."})

        if not turno_esta_disponible(servicio, fecha, hora):
            raise serializers.ValidationError("El horario seleccionado ya no esta disponible.")

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        servicio = validated_data["servicio"]
        fecha = validated_data["fecha"]
        hora = validated_data["hora"]

        # El constraint sala+fecha+hora protege frente a carreras. Si otra
        # reserva gana entre la validacion y el INSERT, se intenta otra sala.
        for _ in range(5):
            sala = obtener_sala_disponible_para_turno(servicio, fecha, hora)
            if sala is None:
                raise serializers.ValidationError("El horario seleccionado ya no esta disponible.")

            try:
                with transaction.atomic():
                    return Turno.objects.create(
                        usuario=request.user,
                        sala=sala,
                        **validated_data,
                    )
            except IntegrityError:
                continue

        raise serializers.ValidationError("No fue posible reservar el horario. Intenta nuevamente.")


class TurnoStaffUpdateSerializer(serializers.ModelSerializer):
    servicio = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.filter(activo=True))

    class Meta:
        model = Turno
        fields = [
            "servicio",
            "fecha",
            "hora",
            "mascota",
            "observaciones",
            "estado",
        ]

    def validate(self, attrs):
        instance = self.instance
        servicio = attrs.get("servicio", instance.servicio)
        fecha = attrs.get("fecha", instance.fecha)
        hora = attrs.get("hora", instance.hora)

        cambia_agenda = any(campo in attrs for campo in ("servicio", "fecha", "hora"))
        if cambia_agenda and not turno_esta_disponible(
            servicio,
            fecha,
            hora,
            exclude_turno_id=instance.pk,
        ):
            raise serializers.ValidationError("No hay una sala disponible para ese servicio y horario.")

        return attrs

    def update(self, instance, validated_data):
        servicio = validated_data.get("servicio", instance.servicio)
        fecha = validated_data.get("fecha", instance.fecha)
        hora = validated_data.get("hora", instance.hora)
        cambia_agenda = any(campo in validated_data for campo in ("servicio", "fecha", "hora"))

        if not cambia_agenda:
            return super().update(instance, validated_data)

        salas = list(
            obtener_salas_disponibles_para_turno(
                servicio,
                fecha,
                hora,
                exclude_turno_id=instance.pk,
            )
        )
        if not salas:
            raise serializers.ValidationError("No hay salas disponibles para ese horario.")

        if instance.sala in salas:
            salas.remove(instance.sala)
            salas.insert(0, instance.sala)
        elif len(salas) > 1:
            random.shuffle(salas)

        for sala in salas:
            try:
                with transaction.atomic():
                    for attr, value in validated_data.items():
                        setattr(instance, attr, value)
                    instance.sala = sala
                    instance.save()
                return instance
            except IntegrityError:
                continue

        raise serializers.ValidationError("No fue posible guardar el turno por una reserva concurrente.")
