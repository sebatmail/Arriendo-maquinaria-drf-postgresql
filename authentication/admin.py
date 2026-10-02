"""
================================================================================
ADMINISTRACIÓN DE USUARIOS EN DJANGO ADMIN
================================================================================
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioCustomAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'razon_social', 'rut_empresa', 'is_staff', 'is_active']
    list_filter = ['rol', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'razon_social', 'rut_empresa']
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Empresa y Roles (EVA-2)', {
            'fields': ('rol', 'rut_empresa', 'razon_social', 'telefono', 'direccion_obra')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Empresa y Roles (EVA-2)', {
            'fields': ('rol', 'rut_empresa', 'razon_social', 'telefono', 'direccion_obra')
        }),
    )
