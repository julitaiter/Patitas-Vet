import random
from datetime import datetime, timedelta

from app.models import DisponibilidadTurno, Sala, Turno


def generar_horarios(hora_inicio, hora_fin, intervalo_minutos):
    horarios = []
    fecha_base = datetime.today().date()
    actual = datetime.combine(fecha_base, hora_inicio)
    fin = datetime.combine(fecha_base, hora_fin)

    while actual < fin:
        horarios.append(actual.time())
        actual += timedelta(minutes=intervalo_minutos)

    return horarios


def _disponibilidades_activas(servicio, fecha):
    if servicio is None or not servicio.activo:
        return DisponibilidadTurno.objects.none()

    return (
        DisponibilidadTurno.objects
        .select_related("sala")
        .filter(
            servicio=servicio,
            sala__activa=True,
            dia_semana=fecha.weekday(),
            activa=True,
        )
    )


def _disponibilidad_contiene_hora(disponibilidad, hora):
    return hora in generar_horarios(
        disponibilidad.hora_inicio,
        disponibilidad.hora_fin,
        disponibilidad.intervalo_minutos,
    )


def obtener_salas_disponibles_para_turno(
    servicio,
    fecha,
    hora,
    exclude_turno_id=None,
):
    sala_ids = {
        disponibilidad.sala_id
        for disponibilidad in _disponibilidades_activas(servicio, fecha)
        if _disponibilidad_contiene_hora(disponibilidad, hora)
    }
    if not sala_ids:
        return []

    turnos_ocupados = Turno.objects.filter(
        sala_id__in=sala_ids,
        fecha=fecha,
        hora=hora,
    ).exclude(estado=Turno.ESTADO_CANCELADO)
    if exclude_turno_id:
        turnos_ocupados = turnos_ocupados.exclude(pk=exclude_turno_id)

    salas_ocupadas = set(turnos_ocupados.values_list("sala_id", flat=True))
    salas_libres = sala_ids - salas_ocupadas
    return list(Sala.objects.filter(pk__in=salas_libres, activa=True).order_by("pk"))


def obtener_sala_disponible_para_turno(
    servicio,
    fecha,
    hora,
    exclude_turno_id=None,
):
    salas = obtener_salas_disponibles_para_turno(
        servicio,
        fecha,
        hora,
        exclude_turno_id=exclude_turno_id,
    )
    return random.choice(salas) if salas else None


def obtener_horarios_disponibles(servicio, fecha):
    horarios_posibles = set()
    for disponibilidad in _disponibilidades_activas(servicio, fecha):
        horarios_posibles.update(generar_horarios(
            disponibilidad.hora_inicio,
            disponibilidad.hora_fin,
            disponibilidad.intervalo_minutos,
        ))

    return sorted(
        hora for hora in horarios_posibles
        if obtener_salas_disponibles_para_turno(servicio, fecha, hora)
    )


def turno_esta_disponible(servicio, fecha, hora, exclude_turno_id=None):
    return bool(obtener_salas_disponibles_para_turno(
        servicio,
        fecha,
        hora,
        exclude_turno_id=exclude_turno_id,
    ))
