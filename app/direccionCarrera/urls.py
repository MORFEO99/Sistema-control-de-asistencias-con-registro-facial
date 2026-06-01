from django.urls import path, include
from . import views

app_name = 'direccionCarrera'

urlpatterns = [
    path("", views.perfil, name="perfil"),
    path('gestion-estudiantes/', views.gestion_estudiantes, name='gestion_estudiantes'),
    path('gestion-estudiantes/crear/', views.crear_estudiante, name='crear_estudiante'),
    path('gestion-estudiantes/editar/<int:pk>/', views.editar_estudiante, name='editar_estudiante'),
    path('gestion-estudiantes/eliminar/<int:pk>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    #---------------------------
    path('gestion-docentes/', views.gestion_docentes, name='gestion_docentes'),
    path('gestion-docentes/crear/', views.crear_docente, name='crear_docente'),
    path('gestion-docentes/editar/<int:pk>/', views.editar_docente, name='editar_docente'),
    path('gestion-docentes/eliminar/<int:pk>/', views.eliminar_docente, name='eliminar_docente'),
]

