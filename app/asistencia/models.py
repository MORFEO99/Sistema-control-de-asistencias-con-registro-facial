from django.db import models
from app.estudiante.models import Estudiante
from app.academico.models import AsignacionDocente

# Create your models here.

class Asistencia(models.Model):
    id = models.AutoField(primary_key=True)  
    fecha_ingreso = models.DateField(auto_now_add=True)
    hora_ingreso = models.TimeField(auto_now_add=True)

    asignacion_docente = models.ForeignKey(AsignacionDocente, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
 
    def __str__(self):
        return f"{self.estudiante} - {self.asignacion_docente} - {self.hora_ingreso}"