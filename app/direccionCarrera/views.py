from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.usuarios.models import Usuario
from app.estudiante.models import Estudiante
from app.direccionCarrera.models import DireccionCarrera
from app.academico.models import Semestre, Paralelo
from app.docente.models import Docente
import logging
logger = logging.getLogger('auditoria')

from .forms import(
    EstudianteCreacionForm, EstudianteEdicionForm, DocenteCreacionForm, DocenteEdicionForm
)
def perfil(request):
    cod_usuario = request.session.get('usuario')
    if not cod_usuario:
        return redirect('index') 
    try:
        direccionCarrera= DireccionCarrera.objects.select_related("usuario").get(usuario__codUsuario=cod_usuario)
    except DireccionCarrera.DoesNotExist:
        return redirect('index')

    return render(request, "direccionCarrera/perfil.html", {"direccionCarrera": direccionCarrera})


# ---------- Listado de estudiantes ----------

def gestion_estudiantes(request):
    estudiantes = Estudiante.objects.select_related('usuario', 'carrera', 'paralelo', 'semestre').all()
    
    semestre_id = request.GET.get('semestre')
    paralelo_id = request.GET.get('paralelo')
    
    if semestre_id:
        estudiantes = estudiantes.filter(semestre_id=semestre_id)
    if paralelo_id:
        estudiantes = estudiantes.filter(paralelo_id=paralelo_id)
    
    context = {
        'estudiantes': estudiantes,
        'semestres': Semestre.objects.all(),
        'paralelos': Paralelo.objects.all(),
        'semestre_seleccionado': int(semestre_id) if semestre_id else None,
        'paralelo_seleccionado': int(paralelo_id) if paralelo_id else None,
    }
    return render(request, 'direccionCarrera/gestion_estudiantes.html', context)

# ---------- Crear estudiante ----------
def crear_estudiante(request):
    if request.method == 'POST':
        form = EstudianteCreacionForm(request.POST, request.FILES)
        if form.is_valid():
            estudiante_creado = form.save()  # guardamos la instancia
            usuario_actual = request.session.get('usuario')
            logger.info(f"Usuario {usuario_actual} creó al estudiante con RU {estudiante_creado.RU}")
            messages.success(request, 'Estudiante creado con éxito.')
            return redirect('direccionCarrera:gestion_estudiantes')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EstudianteCreacionForm()
    return render(request, 'direccionCarrera/crear_estudiante.html', {'form': form})

# ---------- Editar estudiante ----------

def editar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteEdicionForm(request.POST, request.FILES, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante actualizado correctamente.')
            return redirect('direccionCarrera:gestion_estudiantes')
    else:
        form = EstudianteEdicionForm(instance=estudiante)
    return render(request, 'direccionCarrera/editar_estudiante.html', {'form': form, 'estudiante': estudiante})

# ---------- Eliminar estudiante ----------
def eliminar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        usuario = estudiante.usuario
        estudiante.delete()
        usuario.delete()  # Elimina también el usuario asociado
        messages.success(request, 'Estudiante eliminado correctamente.')
        return redirect('direccionCarrera:gestion_estudiantes')
    return render(request, 'direccionCarrera/eliminar_estudiante.html', {'estudiante': estudiante})

# ---------- Listado de docentes ----------
def gestion_docentes(request):
    docentes = Docente.objects.select_related('usuario', 'carrera').prefetch_related(
        'asignaciondocente_set__materia',
        'asignaciondocente_set__paralelo__semestre'
    )

    semestre_id = request.GET.get('semestre')
    paralelo_id = request.GET.get('paralelo')

    if semestre_id:
        docentes = docentes.filter(
            asignaciondocente__paralelo__semestre_id=semestre_id
        )

    if paralelo_id:
        docentes = docentes.filter(
            asignaciondocente__paralelo_id=paralelo_id
        )

    docentes = docentes.distinct()
    context = {
        'docentes': docentes,
        'semestres': Semestre.objects.all(),
        'paralelos': Paralelo.objects.all(),
        'semestre_seleccionado': int(semestre_id) if semestre_id else None,
        'paralelo_seleccionado': int(paralelo_id) if paralelo_id else None,
    }

    return render(request, 'direccionCarrera/gestion_docentes.html', context)

# ---------- Crear docente ----------
def crear_docente(request):
    if request.method == 'POST':
        form = DocenteCreacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Docente creado con éxito.')
            return redirect('direccionCarrera:gestion_docentes')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = DocenteCreacionForm()
    return render(request, 'direccionCarrera/crear_docente.html', {'form': form})

# ---------- Editar docente ----------
def editar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        form = DocenteEdicionForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Docente actualizado correctamente.')
            return redirect('direccionCarrera:gestion_docentes')
    else:
        form = DocenteEdicionForm(instance=docente)
    return render(request, 'direccionCarrera/editar_docente.html', {'form': form, 'docente': docente})

# ---------- Eliminar docente ----------
def eliminar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        usuario = docente.usuario
        docente.delete()
        usuario.delete()
        messages.success(request, 'Docente eliminado correctamente.')
        return redirect('direccionCarrera:gestion_docentes')
    return render(request, 'direccionCarrera/eliminar_docente.html', {'docente': docente})