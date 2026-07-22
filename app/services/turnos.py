from datetime import datetime, timedelta

from app.models import DisponibilidadTurno, Turno


def generar_horarios(hora_inicio, hora_fin, intervalo_minutos):
    horarios = []

    fecha_base = datetime.today().date()
    actual = datetime.combine(fecha_base, hora_inicio)
    fin = datetime.combine(fecha_base, hora_fin)

    while actual < fin:
        horarios.append(actual.time())
        actual += timedelta(minutes=intervalo_minutos)

    return horarios


def obtener_horarios_disponibles(sala, fecha):
    dia_semana = fecha.weekday()

    disponibilidades = DisponibilidadTurno.objects.filter(
        sala=sala,
        dia_semana=dia_semana,
        activa=True,
    )

    horarios_posibles = []

    for disponibilidad in disponibilidades:
        horarios_posibles.extend(
            generar_horarios(
                disponibilidad.hora_inicio,
                disponibilidad.hora_fin,
                disponibilidad.intervalo_minutos,
            )
        )

    horarios_ocupados = set(
        Turno.objects.filter(
            sala=sala,
            fecha=fecha,
        )
        .exclude(estado=Turno.ESTADO_CANCELADO)
        .values_list("hora", flat=True)
    )

    horarios_disponibles = [
        hora for hora in horarios_posibles
        if hora not in horarios_ocupados
    ]

    return sorted(horarios_disponibles)


def turno_esta_disponible(sala, fecha, hora):
    horarios_disponibles = obtener_horarios_disponibles(sala, fecha)

    return hora in horarios_disponibles
