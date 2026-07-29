import django.db.models.deletion
from django.db import migrations, models


def asociar_disponibilidades_a_servicios(apps, schema_editor):
    DisponibilidadTurno = apps.get_model("app", "DisponibilidadTurno")
    Servicio = apps.get_model("app", "Servicio")

    for disponibilidad in DisponibilidadTurno.objects.all().iterator():
        servicios = list(
            Servicio.objects.filter(sala_id=disponibilidad.sala_id).order_by("pk")
        )
        if not servicios:
            disponibilidad.delete()
            continue

        disponibilidad.servicio_id = servicios[0].pk
        disponibilidad.save(update_fields=["servicio"])

        for servicio in servicios[1:]:
            DisponibilidadTurno.objects.create(
                servicio_id=servicio.pk,
                sala_id=disponibilidad.sala_id,
                dia_semana=disponibilidad.dia_semana,
                hora_inicio=disponibilidad.hora_inicio,
                hora_fin=disponibilidad.hora_fin,
                intervalo_minutos=disponibilidad.intervalo_minutos,
                activa=disponibilidad.activa,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_disponibilidadturno_sala_alter_turno_options_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="disponibilidadturno",
            name="disponibilidad_unica_por_sala_dia_horario",
        ),
        migrations.AddField(
            model_name="disponibilidadturno",
            name="servicio",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="disponibilidades",
                to="app.servicio",
            ),
        ),
        migrations.RunPython(
            asociar_disponibilidades_a_servicios,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="disponibilidadturno",
            name="servicio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="disponibilidades",
                to="app.servicio",
            ),
        ),
        migrations.AlterModelOptions(
            name="disponibilidadturno",
            options={
                "ordering": ["servicio", "sala", "dia_semana", "hora_inicio"],
                "verbose_name": "disponibilidad de turno",
                "verbose_name_plural": "disponibilidades de turnos",
            },
        ),
        migrations.AddConstraint(
            model_name="disponibilidadturno",
            constraint=models.UniqueConstraint(
                fields=("servicio", "sala", "dia_semana", "hora_inicio", "hora_fin"),
                name="disponibilidad_unica_por_servicio_sala_dia_horario",
            ),
        ),
        migrations.RemoveField(
            model_name="servicio",
            name="sala",
        ),
    ]
