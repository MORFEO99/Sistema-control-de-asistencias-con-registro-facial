from django.urls import path, include
from . import views

app_name = 'estudiante'

urlpatterns = [
    path('', views.perfil, name='perfil'),
    path('Asignacion-materias/', views.Asignacion_materias, name='asignacion_materias'),
    path('horario/', views.horario, name='horario'),
]