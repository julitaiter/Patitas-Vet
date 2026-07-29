from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_disponibilidad_por_servicio_y_sala"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="turno",
            name="turno_unico_por_sala_fecha_hora",
        ),
        migrations.AddConstraint(
            model_name="turno",
            constraint=models.UniqueConstraint(
                condition=~models.Q(estado="cancelado"),
                fields=("sala", "fecha", "hora"),
                name="turno_unico_por_sala_fecha_hora",
            ),
        ),
    ]
