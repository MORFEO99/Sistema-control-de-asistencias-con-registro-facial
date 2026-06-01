from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    codUsuario = models.CharField(max_length=10, primary_key=True)
    password = models.CharField(max_length=128)  # Antes max_length=10

    def save(self, *args, **kwargs):
        # Si la contraseña no tiene formato de hash, la hasheamos
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.codUsuario