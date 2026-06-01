from django.shortcuts import render, redirect
from app.docente.models import Docente
from app.academico.models import AsignacionDocente, Semestre

def get_docente_actual(request):
    cod_usuario = request.session.get('usuario')
    if not cod_usuario:
        return None
    try:
        return Docente.objects.select_related("usuario").get(usuario__codUsuario=cod_usuario)
    except Docente.DoesNotExist:
        return None
    
    
def perfil(request):
    docente = get_docente_actual(request)
    if not docente:
        return redirect('index')

    semestres = Semestre.objects.filter(
        paralelo__asignaciondocente__docente=docente
    ).distinct()

    return render(request, "docente/perfil.html", {
        "docente": docente,
        "semestres": semestres
    })




def asignacionMaterias(request):
    docente = get_docente_actual(request)
    if not docente:
        return redirect('index')
    asignaciones = AsignacionDocente.objects.filter(docente=docente).select_related(
        "paralelo", "materia", "paralelo__semestre", "paralelo__aula", "horario"
    )
    return render(request, "docente/asignacion.html", {"docente": docente, "asignaciones": asignaciones})
