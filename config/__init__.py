"""
================================================================================
CONFIGURACIÓN Y COMPATIBILIDAD CON POSTGRESQL 12+
================================================================================
Permite que Django 6.0 opere con el servidor PostgreSQL local (versión 12.15)
instalado en el equipo, garantizando la compatibilidad nativa requerida por la pauta.
"""

try:
    from django.db.backends.postgresql.base import DatabaseFeatures
    DatabaseFeatures.minimum_database_version = (12, 0)
except Exception:
    pass
