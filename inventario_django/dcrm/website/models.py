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


class LogAuditoria(models.Model):
    ACCIONES = (
        ('LOGIN',    'Inicio de sesión'),
        ('LOGOUT',   'Cierre de sesión'),
        ('REGISTRO', 'Registro de usuario'),
        ('EDICION',  'Edición de usuario'),
        ('ELIMINACION', 'Eliminación de usuario'),
    )
    usuario    = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    accion     = models.CharField(max_length=20, choices=ACCIONES)
    detalle    = models.TextField(blank=True)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    fecha      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'

    def __str__(self):
        return f"{self.fecha} | {self.usuario} | {self.accion}"