from django.db import models

class Semestre(models.Model):
    codSemestre= models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"
    
class Horario(models.Model):
    codHorario = models.AutoField(primary_key=True)
    dia = models.CharField(max_length=2, choices=[("LU","Lunes"),("MA","Martes"),("MI","Miércoles"),("JU","Jueves"),("VI","Viernes")])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    def __str__(self):
        return f"{self.get_dia_display()} {self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"

class Materia(models.Model):
    codMateria= models.AutoField(primary_key= True)
    materiaID = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}"

class Aula(models.Model):
    codAula = models.AutoField(primary_key=True)
    
    def __str__(self):
        return f"{self.codAula}"

class Carrera(models.Model):
    codCarrera = models.CharField(max_length=5, primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"
    

class Paralelo(models.Model):
    codParalelo = models.AutoField(primary_key= True)
    numeroParalelo = models.CharField(max_length=10)
    aula = models.ForeignKey(Aula, on_delete= models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.numeroParalelo}"


    

class AsignacionDocente(models.Model):
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    docente = models.ForeignKey("docente.Docente", on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete= models.CASCADE)

    def __str__(self):
        return f"{self.paralelo} - {self.materia} - {self.horario} - {self.docente}"
