"""
================================================================================
ENRUTADOR PRINCIPAL DEL PROYECTO (EVA-2 ARRIENDO DE MAQUINARIA)
================================================================================
Configuración unificada de URLs para servicios RESTful (DRF), documentación Swagger
y vistas renderizadas de frontend.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Panel de Administración Nativo de Django
    path('admin/', admin.site.urls),

    # Endpoints de Autenticación y JWT (Claims de Rol)
    path('api/auth/', include('authentication.urls')),

    # Endpoints Principales de la API de Renting (Matriz de Permisos EVA-2)
    path('api/', include('renting.urls')),

    # ==========================================================================
    # DOCUMENTACIÓN TÉCNICA OPENAPI / SWAGGER (Cumplimiento Pauta Técnica)
    # ==========================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Interfaz Web Interactiva (Templates con Footer de Estudiante)
    path('', include('web_ui.urls')),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
]
