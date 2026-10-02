"""
================================================================================
RUTAS DE AUTENTICACIÓN (API)
================================================================================
"""

from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    RegistroUsuarioView,
    PerfilUsuarioView
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
]
