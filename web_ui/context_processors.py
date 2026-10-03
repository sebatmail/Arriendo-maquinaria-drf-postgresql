"""
================================================================================
CONTEXT PROCESSORS - METADATOS CORPORATIVOS DE PORTAFOLIO
================================================================================
Inyecta la identidad corporativa de la plataforma RENT-EQUIP PRO en todos los
templates del sistema.
"""

from django.conf import settings

def enterprise_footer_info(request):
    """
    Inyecta metadatos empresariales en el contexto de renderizado HTML.
    """
    return {
        'plataforma_info': getattr(settings, 'PLATAFORMA_INFO', {
            'NOMBRE_PLATAFORMA': 'RENT-EQUIP PRO',
            'ORGANIZACION': 'Momentum Space Cloud Solutions',
            'DOMINIO': 'proyecto-backend.momentumspace.cl',
            'VERSION': 'v2.4.0 Enterprise',
            'ANO': '2026',
            'CONTACTO_SOPORTE': 'soporte@momentumspace.cl',
        })
    }
