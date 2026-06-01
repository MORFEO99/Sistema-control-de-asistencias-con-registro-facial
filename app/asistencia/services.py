from datetime import datetime
from app.asistencia.models import Asistencia
from app.academico.models import AsignacionDocente


def obtener_dia_actual():
    dias = {
        0: "LU",
        1: "MA",
        2: "MI",
        3: "JU",
        4: "VI",
        5: "SA",
        6: "DO",
    }
    return dias[datetime.now().weekday()]


def registrar_asistencia(estudiante):
    ahora = datetime.now()
    hora_actual = ahora.time()
    dia_actual = obtener_dia_actual()

    # obtener asignaciones del estudiante para el dia actual
    asignaciones = AsignacionDocente.objects.filter(
        paralelo=estudiante.paralelo,
        horario__dia=dia_actual
    )

    for asignacion in asignaciones:
        inicio = asignacion.horario.hora_inicio
        fin = asignacion.horario.hora_fin

        #validar si la hora actual esta dentro del rango de la clase
        if inicio <= hora_actual <= fin:

            # evitar doble registro
            existe = Asistencia.objects.filter(
                estudiante=estudiante,
                asignacion_docente=asignacion,
                fecha_ingreso=ahora.date()
            ).exists()

            if existe:
                return None, f"Ya te registraste asistencia en {asignacion.materia.nombre}"

            # crear asistencia
            asistencia = Asistencia.objects.create(
                estudiante=estudiante,
                asignacion_docente=asignacion
            )

            return asistencia, f"Asistencia registrada en {asignacion.materia.nombre}"

    # horario no vallido
    return None, "No tienes clase en este horario"