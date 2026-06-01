from django.urls import path, include
from . import views

app_name = 'docente'

urlpatterns = [
    path('', views.perfil, name='perfil'),
    path('clases-asignadas/', views.asignacionMaterias, name='asignacion'),
]