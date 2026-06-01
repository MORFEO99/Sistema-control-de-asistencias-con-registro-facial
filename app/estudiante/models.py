from django.db import models
from app.usuarios.models import Usuario
from app.academico.models import Carrera, Paralelo, Semestre

class Estudiante(models.Model):
    RU = models.IntegerField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    correo_institucional = models.EmailField(unique=True)
    telefono = models.IntegerField()
    foto = models.ImageField(upload_to="rostros/", null=True, blank=True)
    
    encoding = models.TextField(null=True, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
