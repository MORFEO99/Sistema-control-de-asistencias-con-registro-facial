from django.db import models
from app.usuarios.models import Usuario

class Docente(models.Model):
    codDocente = models.IntegerField(primary_key=True)
    usuario= models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField()
    correo_institucional = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField()
    carrera = models.ForeignKey("academico.Carrera", on_delete=models.CASCADE)