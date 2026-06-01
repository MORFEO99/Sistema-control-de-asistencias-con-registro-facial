from django.shortcuts import render
from django.utils import timezone
from itertools import groupby
from .utils import render_to_pdf

from django.shortcuts import get_object_or_404
from app.estudiante.models import Estudiante
from app.docente.models import Docente
from .services import obtener_asistencias
from app.academico.models import Paralelo, Semestre, Materia, AsignacionDocente
from app.direccionCarrera.models import DireccionCarrera
from django.db.models import Count

from django.templatetags.static import static


#-------------Reportes para dirección de carrera------------------
def reporte_direccionCarrera_global(request):
    semestre = request.GET.get("semestre")
    paralelo = request.GET.get("paralelo")

    # filtros
    asistencias = obtener_asistencias(
        semestre=semestre,
        paralelo=paralelo
    )
    #datos
    asistencias = asistencias.values(
        "estudiante__RU",
        "estudiante__nombre",
        "estudiante__apellido",
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "asignacion_docente__materia__nombre",
        "hora_ingreso",
        "fecha_ingreso"
    ).annotate(
        total_asistencias=Count("id")
    ).order_by(
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "estudiante__apellido",
        "fecha_ingreso",
    )

    return render(request, "reporteAsistencia/reporteGlobal_direccionCarrera.html", {
        "asistencias": asistencias,
        "semestres": Semestre.objects.all(),
        "paralelos": Paralelo.objects.all(),
        "materias": Materia.objects.all(),
        "semestre_seleccionado": int(semestre) if semestre else None,
        "paralelo_seleccionado": int(paralelo) if paralelo else None,
    })


def exportar_direccionCarrera_global_pdf(request):

    asistencias = obtener_asistencias().order_by(
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "estudiante__apellido"
    )
    logo_url = request.build_absolute_uri(static("logoSalesiana.png"))

    data = []
    # Agrupar por semestre, luego por paralelo, luego por estudiante
    for semestre, sem_group in groupby(asistencias, key=lambda x: x.estudiante.semestre):
        sem_data = {"semestre": semestre, "paralelos": []}

        for paralelo, par_group in groupby(sem_group, key=lambda x: x.estudiante.paralelo):
            par_data = {"paralelo": paralelo, "estudiantes": []}

            for estudiante, est_group in groupby(par_group, key=lambda x: x.estudiante):
                par_data["estudiantes"].append({
                    "estudiante": estudiante,
                    "asistencias": list(est_group)
                })

            sem_data["paralelos"].append(par_data)

        data.append(sem_data)
    #identificar al usuario para mostrar su nombre en el reporte
    cod_usuario = request.session.get("usuario")
    direccion = None
    if cod_usuario:
        try:
            direccion = DireccionCarrera.objects.select_related("carrera").get(
                usuario__codUsuario=cod_usuario
            )
        except DireccionCarrera.DoesNotExist:
            direccion = None
    return render_to_pdf("reporteAsistencia/pdf_global_direccionCarrera.html", {
        "data": data,
        "logo_url": logo_url,
        "hoy": timezone.localtime(timezone.now()).date(),
        "direccion": direccion
    })
#-------------------------------------------------

def reporte_direccionCarrera_diario(request):
    hoy = timezone.localtime(timezone.now()).date()
    semestre = request.GET.get("semestre")
    paralelo = request.GET.get("paralelo")

    # filtros 
    asistencias = obtener_asistencias(
        fecha=hoy,  
        semestre=semestre,
        paralelo=paralelo   
    )

    # estudiantes presentes hoy 
    asistencias = asistencias.values(
        "estudiante__RU",
        "estudiante__nombre",
        "estudiante__apellido",
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "asignacion_docente__materia__nombre",
        "asignacion_docente__paralelo__numeroParalelo",
        "hora_ingreso"
    ).annotate(
        total_asistencias=Count("id")
        #agrupar por estudiante
    ).order_by(
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "estudiante__apellido"
    )
    return render(request, "reporteAsistencia/reporteDiario_direccionCarrera.html", {
        "asistencias": asistencias,
        "semestres": Semestre.objects.all(),
        "paralelos": Paralelo.objects.all(),
        "materias": Materia.objects.all(),
        "semestre_seleccionado": int(semestre) if semestre else None,
        "paralelo_seleccionado": int(paralelo) if paralelo else None,
        "hoy": hoy
    })



def exportar_direccionCarrera_diario_pdf(request):
    hoy = timezone.localtime(timezone.now()).date()

    # Asistencias del dia
    asistencias = obtener_asistencias(fecha=hoy).order_by(
        "estudiante__semestre__nombre",
        "estudiante__paralelo__numeroParalelo",
        "estudiante__apellido"
    )
    logo_url = request.build_absolute_uri(static("logoSalesiana.png"))
    data = []
    # Agrupar por semestre, luego por paralelo, luego por estudiante
    for semestre, sem_group in groupby(asistencias, key=lambda x: x.estudiante.semestre):
        sem_data = {"semestre": semestre, "paralelos": []}

        for paralelo, par_group in groupby(sem_group, key=lambda x: x.estudiante.paralelo):
            par_data = {"paralelo": paralelo, "estudiantes": []}

            for estudiante, est_group in groupby(par_group, key=lambda x: x.estudiante):
                par_data["estudiantes"].append({
                    "estudiante": estudiante,
                    "asistencias": list(est_group)
                })

            sem_data["paralelos"].append(par_data)

        data.append(sem_data)

    cod_usuario = request.session.get("usuario")
    direccion = None
    if cod_usuario:
        try:
            direccion = DireccionCarrera.objects.select_related("carrera").get(
                usuario__codUsuario=cod_usuario
            )
        except DireccionCarrera.DoesNotExist:
            direccion = None
    return render_to_pdf("reporteAsistencia/pdf_diario_direccionCarrera.html", {
        "data": data,
        "hoy": hoy,
        "logo_url": logo_url,
        "direccion": direccion
    })


#-------------Reportes para estudiante------------------
def reporte_estudiante(request, ru):
    estudiante = get_object_or_404(Estudiante, RU=ru)
    asistencias = obtener_asistencias(estudiante=estudiante).order_by("fecha_ingreso")
    data = []
    for fecha, grupo in groupby(asistencias, key=lambda x: x.fecha_ingreso):
        data.append({
            "fecha": fecha,
            "asistencias": list(grupo)
        })

    return render(request, "reporteAsistencia/reporte_estudiante.html", {
        "data": data,
        "estudiante": estudiante,
        "asistencias": asistencias   
    })

def exportar_estudiante_pdf(request, ru):
    estudiante = get_object_or_404(Estudiante, RU=ru)
    asistencias = obtener_asistencias(estudiante=estudiante).order_by("fecha_ingreso")
    logo_url = request.build_absolute_uri(static("logoSalesiana.png"))

    # Agrupar por fecha
    data = []
    for fecha, grupo in groupby(asistencias, key=lambda x: x.fecha_ingreso):
        data.append({
            "fecha": fecha,
            "asistencias": list(grupo)
        })

    return render_to_pdf("reporteAsistencia/pdf_ReporteEstudiante.html", {
        "data": data,
        "estudiante": estudiante,
        "asistencias": asistencias, 
        "hoy": timezone.localtime(timezone.now()).date(),
        "logo_url":logo_url
    })


#-------------Reportes para docente------------------
def reporte_docente_diario(request, codDocente):
    hoy = timezone.localtime(timezone.now()).date()
    docente = get_object_or_404(Docente, codDocente=codDocente)

    asistencias = obtener_asistencias(fecha=hoy).filter(
        asignacion_docente__docente=docente
    ).order_by("hora_ingreso")

    materias = AsignacionDocente.objects.filter(docente=docente).select_related("materia")

    return render(request, "reporteAsistencia/reporteDiario_docente.html", {
        "docente": docente,
        "asistencias": asistencias,
        "materias": materias,
        "hoy": hoy
    })

def reporte_docente_global(request, codDocente):
    docente = get_object_or_404(Docente, codDocente=codDocente)

    # filstrar las asistencias del docente y ordenarlas por fecha
    asistencias = obtener_asistencias(docente=docente).filter(
        asignacion_docente__docente=docente
    ).order_by("fecha_ingreso")

    data = []
    for fecha, group in groupby(asistencias, key=lambda x: x.fecha_ingreso):
        data.append({
            "fecha": fecha,
            "asistencias": list(group)
        })
    materias = AsignacionDocente.objects.filter(docente=docente).select_related("materia")

    return render(request, "reporteAsistencia/reporteGlobal_docente.html", {
        "docente": docente,
        "data": data,
        "materias": materias,
        "hoy": timezone.localtime(timezone.now()).date(),
        "asistencias": asistencias
    })
#--------------------------------------------------
def exportar_docente_global_pdf(request, codDocente):
    docente = get_object_or_404(Docente, codDocente=codDocente)
    #filstrar las asistencias del docente y ordenarlas por fecha
    asistencias = obtener_asistencias(docente=docente).filter(
        asignacion_docente__docente=docente
    ).order_by("fecha_ingreso", "hora_ingreso")
    logo_url = request.build_absolute_uri(static("logoSalesiana.png"))

    #  agrupar por fecha
    data = []
    for fecha, group in groupby(asistencias, key=lambda x: x.fecha_ingreso):
        data.append({
            "fecha": fecha,
            "asistencias": list(group)
        })

    # obtener materias asignadas al docente
    materias = AsignacionDocente.objects.filter(docente=docente).select_related("materia")

    return render_to_pdf("reporteAsistencia/pdf_global_docente.html", {
        "docente": docente,
        "data": data,
        "materias": materias,
        "logo_url": logo_url,
        "hoy": timezone.localtime(timezone.now()).date()
    })

def exportar_docente_diario_pdf(request, codDocente):
    hoy = timezone.localtime(timezone.now()).date()
    docente = get_object_or_404(Docente, codDocente=codDocente)

    #filstrar las asistencias del docente para el día actual y ordenarlas por hora
    asistencias = obtener_asistencias(fecha=hoy).filter(
        asignacion_docente__docente=docente
    ).order_by("hora_ingreso")
    logo_url = request.build_absolute_uri(static("logoSalesiana.png"))

    # obtener materias asignadas al docente
    materias = AsignacionDocente.objects.filter(docente=docente).select_related("materia")

    return render_to_pdf("reporteAsistencia/pdf_diario_docente.html", {
        "docente": docente,
        "asistencias": asistencias,
        "materias": materias,
        "hoy": hoy,       
        "logo_url": logo_url
    })