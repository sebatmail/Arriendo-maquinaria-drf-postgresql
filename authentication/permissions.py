"""
================================================================================
CLASES DE PERMISOS PERSONALIZADOS (RBAC PARA DRF)
================================================================================
Implementa la matriz de control de acceso basada en roles solicitada en la pauta:
- Lectura pública de catálogo
- Gestión de carro y transacciones exclusiva para Empresas Constructoras
- Gestión de inventario, flota y transición de estados para Ejecutivos de Arriendos
"""

from rest_framework import permissions
from .models import RolUsuario

class IsEmpresaConstructora(permissions.BasePermission):
    """
    Permite acceso únicamente a usuarios autenticados con rol de Empresa Constructora.
    """
    message = "Acceso denegado: Esta acción está reservada exclusivamente para Empresas Constructoras (Clientes)."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.rol == RolUsuario.EMPRESA_CONSTRUCTORA or request.user.is_superuser)
        )


class IsEjecutivoArriendos(permissions.BasePermission):
    """
    Permite acceso únicamente a Administradores / Ejecutivos de Arriendos.
    """
    message = "Acceso denegado: Esta acción requiere permisos de Ejecutivo de Arriendos / Administrador."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.rol == RolUsuario.EJECUTIVO_ARRIENDOS or request.user.is_staff or request.user.is_superuser)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura pública (GET, HEAD, OPTIONS) a cualquier usuario o visitante,
    pero restringe las mutaciones (POST, PUT, PATCH, DELETE) a Ejecutivos / Admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.rol == RolUsuario.EJECUTIVO_ARRIENDOS or request.user.is_staff or request.user.is_superuser)
        )


class IsDocAdminUser(permissions.BasePermission):
    """
    Permiso específico según requerimiento de clase: La documentación Swagger/OpenAPI
    solo puede ser vista por administradores o mediante header de autorización admin.
    """
    message = "Acceso restringido: La documentación Swagger/OpenAPI es de acceso exclusivo para Administradores."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.rol == RolUsuario.EJECUTIVO_ARRIENDOS or request.user.is_staff or request.user.is_superuser)
        )
