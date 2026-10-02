"""
================================================================================
CONTEXT PROCESSORS - METADATOS Y FOOTER DEL ESTUDIANTE (EVA-2)
================================================================================
Permite la inyección global de las variables de autoría del estudiante en todos
los templates del sistema, garantizando el cumplimiento de la pauta de evaluación.
"""

from django.conf import settings

def evaluacion_footer_info(request):
    """
    Inyecta datos institucionales y de autoría en el contexto de renderizado HTML.
    """
    return {
        'alumno_info': getattr(settings, 'ALUMNO_INFO', {
            'NOMBRE_COMPLETO': 'Sebastián Tapia',
            'SECCION': 'Backend DLY01',
            'ANO': '2026',
            'PROYECTO': 'Proyecto 6: Arriendo de Maquinaria de Construcción',
            'ASIGNATURA': 'Desarrollo Backend (EVA-2)',
        })
    }
