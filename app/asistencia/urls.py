from django.urls import path
from . import views

urlpatterns = [
    path('asistencia/', views.tomar_asistencia, name='tomar_asistencia'),
    
]