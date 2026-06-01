from django.shortcuts import render, redirect
from app.estudiante.models import Estudiante
from app.academico.models import AsignacionDocente
from collections import defaultdict

def get_estudiante_actual(request):
    cod_usuario = request.session.get('usuario')

    if not cod_usuario:
        return None

    try:
        return Estudiante.objects.select_related(
            "usuario", "paralelo__semestre"
        ).get(usuario__codUsuario=cod_usuario)
    except Estudiante.DoesNotExist:
        return None



def perfil(request):
    cod_usuario = request.session.get('usuario')

    if not cod_usuario:
        return redirect('index')  # si no está logueado

    try:
        estudiante = Estudiante.objects.select_related("usuario").get(usuario__codUsuario=cod_usuario)
    except Estudiante.DoesNotExist:
        return redirect('index')

    return render(request, "estudiante/perfil.html", {"estudiante": estudiante})

def Asignacion_materias(request):
    estudiante = get_estudiante_actual(request)

    if not estudiante:
        return redirect('index')

    asignaciones = AsignacionDocente.objects.filter(
        paralelo=estudiante.paralelo
    ).select_related(
        "materia",
        "docente",
    )

    return render(request, "estudiante/asignacion_materias.html", {
        "estudiante": estudiante,
        "asignaciones":asignaciones,
    })

def horario(request):
    estudiante = get_estudiante_actual(request)

    if not estudiante:
        return redirect('index')

    asignaciones = AsignacionDocente.objects.filter(
        paralelo=estudiante.paralelo
    ).select_related("horario", "materia")

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    horario_dict = defaultdict(lambda: {dia: "" for dia in dias})

    for asignacion in asignaciones:
        dia = asignacion.horario.get_dia_display()
        rango = f"{asignacion.horario.hora_inicio.strftime('%H:%M')} - {asignacion.horario.hora_fin.strftime('%H:%M')}"
        horario_dict[rango][dia] = asignacion.materia.nombre

    # Convertir a lista ordenada con materias en orden de días
    horario_ordenado = []
    for rango, materias in sorted(horario_dict.items()):
        fila = [materias[dia] for dia in dias]  # lista en orden de días
        horario_ordenado.append({"rango": rango, "materias": fila})

    return render(request, "estudiante/horario.html", {
        "estudiante": estudiante,
        "horario": horario_ordenado,
        "dias": dias,
    })