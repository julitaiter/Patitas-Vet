from rest_framework import serializers

from app.models import DisponibilidadTurno, Sala, Servicio


class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ["id", "nombre", "descripcion", "activa", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DisponibilidadTurnoSerializer(serializers.ModelSerializer):
    servicio = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.filter(activo=True))
    sala = serializers.PrimaryKeyRelatedField(queryset=Sala.objects.filter(activa=True))
    servicio_nombre = serializers.CharField(source="servicio.nombre", read_only=True)
    sala_nombre = serializers.CharField(source="sala.nombre", read_only=True)
    dia_nombre = serializers.CharField(source="get_dia_semana_display", read_only=True)

    class Meta:
        model = DisponibilidadTurno
        fields = [
            "id",
            "servicio",
            "servicio_nombre",
            "sala",
            "sala_nombre",
            "dia_semana",
            "dia_nombre",
            "hora_inicio",
            "hora_fin",
            "intervalo_minutos",
            "activa",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        instance = self.instance
        servicio = attrs.get("servicio", getattr(instance, "servicio", None))
        sala = attrs.get("sala", getattr(instance, "sala", None))
        dia_semana = attrs.get("dia_semana", getattr(instance, "dia_semana", None))
        hora_inicio = attrs.get("hora_inicio", getattr(instance, "hora_inicio", None))
        hora_fin = attrs.get("hora_fin", getattr(instance, "hora_fin", None))
        intervalo = attrs.get("intervalo_minutos", getattr(instance, "intervalo_minutos", None))

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({"hora_fin": "Debe ser posterior a la hora de inicio."})

        if intervalo is not None and intervalo <= 0:
            raise serializers.ValidationError({"intervalo_minutos": "Debe ser mayor a cero."})

        if servicio and sala and dia_semana is not None and hora_inicio and hora_fin:
            qs = DisponibilidadTurno.objects.filter(
                servicio=servicio,
                sala=sala,
                dia_semana=dia_semana,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe una disponibilidad superpuesta para ese servicio, sala y dia."
                )

        return attrs
