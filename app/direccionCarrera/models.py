from django.db import models
from app.usuarios.models import Usuario
from app.academico.models import Carrera
class DireccionCarrera(models.Model):
    codDireccionCarrera = models.IntegerField(primary_key= True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    correo_intitucional = models.EmailField(unique=True)
    telefono = models.IntegerField()
