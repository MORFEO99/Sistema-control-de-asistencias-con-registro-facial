from app.asistencia.models import Asistencia

def obtener_asistencias(
    fecha=None,
    materia=None,
    paralelo=None,
    semestre=None,
    docente=None,
    estudiante=None
):
    qs = Asistencia.objects.select_related(
        "estudiante",
        "estudiante__paralelo",
        "estudiante__semestre",  # opcional (solo para mostrar)
        "asignacion_docente",
        "asignacion_docente__materia",
        "asignacion_docente__paralelo",
        "asignacion_docente__paralelo__semestre",
        "asignacion_docente__docente"
    )

    if fecha:
        qs = qs.filter(fecha_ingreso=fecha)

    if paralelo:
        qs = qs.filter(asignacion_docente__paralelo__codParalelo=paralelo)

    if semestre:
        qs = qs.filter(asignacion_docente__paralelo__semestre__codSemestre=semestre)

    if docente:
        qs = qs.filter(asignacion_docente__docente=docente)

    if estudiante:
        qs = qs.filter(estudiante=estudiante)

    return qs.order_by("-fecha_ingreso", "-hora_ingreso")