"""
================================================================================
RUTAS DE LA INTERFAZ WEB (TEMPLATES HTML)
================================================================================
"""

from django.urls import path
from .views import (
    index_catalogo_view,
    carro_view,
    mis_contratos_view,
    admin_maquinarias_view,
    admin_contratos_view,
    login_view,
    registro_view,
    logout_view,
    documentacion_admin_view
)

urlpatterns = [
    path('', index_catalogo_view, name='index_catalogo'),
    path('carro/', carro_view, name='carro_view'),
    path('mis-contratos/', mis_contratos_view, name='mis_contratos_view'),
    path('admin/maquinarias/', admin_maquinarias_view, name='admin_maquinarias_view'),
    path('admin/contratos/', admin_contratos_view, name='admin_contratos_view'),
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('documentacion/', documentacion_admin_view, name='documentacion_admin'),
]
