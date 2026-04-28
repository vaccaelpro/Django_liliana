from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('ADMINISTRADOR', 'Administrador'),
        ('APRENDIZ', 'Aprendiz'),
    )
    documento = models.CharField(max_length=20, unique=True, null=True, blank=True)
    rol = models.CharField(max_length=15, choices=ROLES, default='APRENDIZ')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
