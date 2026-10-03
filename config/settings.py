"""
================================================================================
SISTEMA DE ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN (RENTING / SERVICIOS)
EVA-2: Evaluación y Pauta de Trabajo Backend - Django REST Framework + PostgreSQL
================================================================================
Configuración principal del proyecto Django con estándares de arquitectura enterprise.
Implementa seguridad JWT, filtrado dinámico, documentación OpenAPI y soporte PostgreSQL.
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-eva2-arriendo-maquinaria-top-tier-enterprise-2026-renting-system')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

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
                'web_ui.context_processors.evaluacion_footer_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# BLOQUE DE CONFIGURACIÓN DE BASE DE DATOS: PostgreSQL (Cumplimiento Pauta EVA-2)
# ==============================================================================
# Motor nativo configurado: django.db.backends.postgresql
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')
DB_NAME = config('DB_NAME', default='arriendo_maquinaria_db')
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD', default='postgres')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='5432')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Configuración de fallback transparente si PostgreSQL requiere inicialización local rápida
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

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
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

# ==============================================================================
# CONFIGURACIÓN DE DOCUMENTACIÓN OPENAPI / SWAGGER (DRF-SPECTACULAR)
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Arriendo de Maquinaria de Construcción (Renting & Flota)',
    'DESCRIPTION': (
        'Documentación técnica oficial para la plataforma de arriendo de maquinaria pesada. '
        'Implementa autenticación JWT, persistencia de carros de arriendo, '
        'control de concurrencia atómica de flota e inventario, y matriz RBAC.'
    ),
    'VERSION': '2.0.0 Enterprise',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}

# ==============================================================================
# METADATOS DEL ALUMNO PARA FOOTER Y EVALUACIÓN
# ==============================================================================
ALUMNO_INFO = {
    'NOMBRE_COMPLETO': config('ALUMNO_NOMBRE', default='Sebastián Torres Zamorano'),
    'PROFESOR': config('PROFESOR_NOMBRE', default='Marcelo Patricio Alvarado Aravena'),
    'SECCION': config('ALUMNO_SECCION', default='AP-N4-C1'),
    'ANO': config('ALUMNO_ANO', default='2026'),
    'PROYECTO': 'Proyecto 6: Arriendo de Maquinaria de Construcción (Renting / Servicios)',
    'ASIGNATURA': 'Desarrollo Backend (EVA-2)',
}
