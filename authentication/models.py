"""
================================================================================
MÓDULO DE AUTENTICACIÓN Y ROLES (RBAC) - MODELOS
================================================================================
Define el modelo de Usuario personalizado con roles explícitos y atributos
empresariales normalizados (3FN).
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

class RolUsuario(models.TextChoices):
    """
    CHOICES explícitos requeridos por la pauta técnica para el control de roles.
    """
    EMPRESA_CONSTRUCTORA = 'EMPRESA_CONSTRUCTORA', 'Empresa Constructora (Cliente)'
    EJECUTIVO_ARRIENDOS = 'EJECUTIVO_ARRIENDOS', 'Ejecutivo de Arriendos (Administrador/Gestor)'


class Usuario(AbstractUser):
    """
    Modelo de Usuario extendido con soporte para roles RBAC y atributos de cliente B2B.
    """
    rol = models.CharField(
        max_length=30,
        choices=RolUsuario.choices,
        default=RolUsuario.EMPRESA_CONSTRUCTORA,
        help_text='Rol del usuario dentro del ecosistema de renting'
    )
    rut_empresa = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='RUT de la empresa constructora o identificación fiscal'
    )
    razon_social = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text='Nombre de fantasía o razón social de la empresa'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Teléfono de contacto de obra o administrativo'
    )
    direccion_obra = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Dirección principal de faena o despacho'
    )

    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'
        ordering = ['id']

    def save(self, *args, **kwargs):
        """
        Garantiza sincronización de permisos de staff en Django Admin para ejecutivos.
        """
        if self.rol == RolUsuario.EJECUTIVO_ARRIENDOS:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def es_ejecutivo(self) -> bool:
        return self.rol == RolUsuario.EJECUTIVO_ARRIENDOS or self.is_superuser

    @property
    def es_cliente(self) -> bool:
        return self.rol == RolUsuario.EMPRESA_CONSTRUCTORA

    def __str__(self):
        display_name = self.razon_social or self.get_full_name() or self.username
        return f"{display_name} ({self.get_rol_display()})"
