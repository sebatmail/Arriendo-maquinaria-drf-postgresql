"""
================================================================================
RENT-EQUIP PRO | SISTEMA INDUSTRIAL DE ARRIENDO DE MAQUINARIA PESADA
Desarrollado para Plataforma B2B SaaS • Momentum Space
================================================================================
Configuración principal de producción con soporte para MySQL / PostgreSQL,
autenticación JWT RBAC, filtrado dinámico y documentación OpenAPI.
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-rent-equip-pro-momentum-space-enterprise-2026')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'proyecto-backend.momentumspace.cl',
    'www.proyecto-backend.momentumspace.cl',
    'momentumspace.cl',
    'localhost',
    '127.0.0.1',
    '*',
]

CSRF_TRUSTED_ORIGINS = [
    'https://proyecto-backend.momentumspace.cl',
    'http://proyecto-backend.momentumspace.cl',
    'https://*.momentumspace.cl',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de Terceros de Alto Rendimiento
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',

    # Aplicaciones Propias del Dominio de Renting
    'authentication',
    'renting',
    'web_ui',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web_ui.context_processors.enterprise_footer_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS (PRODUCCIÓN / LOCAL)
# ==============================================================================
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')
DB_NAME = config('DB_NAME', default='arriendo_maquinaria_db')
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD', default='postgres')
DB_HOST = config('DB_HOST', default='127.0.0.1')
DB_PORT = config('DB_PORT', default='5432')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
        } if 'mysql' in DB_ENGINE else {},
    }
}

USE_SQLITE_FALLBACK = config('USE_SQLITE_FALLBACK', default=False, cast=bool)
if USE_SQLITE_FALLBACK:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# ==============================================================================
# MODELO DE USUARIO PERSONALIZADO (RBAC)
# ==============================================================================
AUTH_USER_MODEL = 'authentication.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURACIÓN DE DJANGO REST FRAMEWORK (DRF)
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ==============================================================================
# CONFIGURACIÓN DE JSON WEB TOKEN (SIMPLE_JWT)
# ==============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'authentication.serializers.CustomTokenObtainPairSerializer',
}

# Permitir incrustar documentación en iframes del mismo origen
X_FRAME_OPTIONS = 'SAMEORIGIN'

# ==============================================================================
# CONFIGURACIÓN DE DOCUMENTACIÓN OPENAPI / SWAGGER
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Industrial de Arriendo de Maquinaria (RENT-EQUIP PRO)',
    'DESCRIPTION': (
        'Documentación técnica oficial de la plataforma de arriendo y gestión de flota industrial. '
        'Implementa autenticación JWT, persistencia de carros de arriendo en base de datos, '
        'control transaccional atómico de flota e inventario, y matriz RBAC.'
    ),
    'VERSION': '2.4.0 Enterprise',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_DIST': '//unpkg.com/swagger-ui-dist@5.11.0',
    'SWAGGER_UI_FAVICON_HREF': '//unpkg.com/swagger-ui-dist@5.11.0/favicon-32x32.png',
    'REDOC_DIST': '//cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}

# ==============================================================================
# METADATOS CORPORATIVOS DE PORTAFOLIO (MOMENTUM SPACE)
# ==============================================================================
PLATAFORMA_INFO = {
    'NOMBRE_PLATAFORMA': 'RENT-EQUIP PRO',
    'ORGANIZACION': 'Momentum Space',
    'SITIO_WEB': 'https://momentumspace.cl',
    'DOMINIO': 'proyecto-backend.momentumspace.cl',
    'VERSION': 'v2.4.0 Enterprise',
    'ANO': '2026',
    'CONTACTO_SOPORTE': 'storres@momentumspace.cl',
}
