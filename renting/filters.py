"""
================================================================================
FILTROS AVANZADOS MEDIANTE DJANGO-FILTER (EVA-2)
================================================================================
Configura el filtrado declarativo sobre el catálogo de maquinarias y contratos,
permitiendo búsquedas compuestas por categoría, rango de tarifas diarias y disponibilidad.
"""

import django_filters
from django.db.models import Q
from .models import Maquinaria, CategoriaEquipo, ContratoArriendo, EstadoContrato, EstadoMaquinaria

class MaquinariaFilter(django_filters.FilterSet):
    """
    Filtro avanzado para el catálogo de maquinarias.
    Soporta:
    - Filtrado por categoría (id o slug)
    - Rango de precios en tarifa diaria (min_precio, max_precio)
    - Rango de garantía (max_garantia)
    - Filtrado por estado operativo
    - Filtro booleano de disponibilidad real de flota (disponible=true)
    - Búsqueda general de texto
    """
    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaEquipo.objects.all(),
        field_name='categoria',
        label='Categoría de Equipo'
    )
    categoria_slug = django_filters.CharFilter(
        field_name='categoria__slug',
        lookup_expr='iexact',
        label='Slug de Categoría'
    )
    min_precio = django_filters.NumberFilter(
        field_name='tarifa_diaria',
        lookup_expr='gte',
        label='Tarifa Diaria Mínima ($)'
    )
    max_precio = django_filters.NumberFilter(
        field_name='tarifa_diaria',
        lookup_expr='lte',
        label='Tarifa Diaria Máxima ($)'
    )
    max_garantia = django_filters.NumberFilter(
        field_name='monto_garantia',
        lookup_expr='lte',
        label='Monto de Garantía Máxima ($)'
    )
    estado_operativo = django_filters.ChoiceFilter(
        choices=EstadoMaquinaria.choices,
        label='Estado Operativo'
    )
    solo_disponibles = django_filters.BooleanFilter(
        method='filter_solo_disponibles',
        label='Solo unidades con flota disponible > 0'
    )
    q = django_filters.CharFilter(
        method='filter_search',
        label='Búsqueda por texto (Nombre, SKU, Marca, Descripción)'
    )

    class Meta:
        model = Maquinaria
        fields = [
            'categoria',
            'categoria_slug',
            'min_precio',
            'max_precio',
            'max_garantia',
            'estado_operativo',
            'solo_disponibles',
            'q'
        ]

    def filter_solo_disponibles(self, queryset, name, value):
        if value:
            return queryset.filter(
                flota_disponible__gt=0,
                estado_operativo=EstadoMaquinaria.DISPONIBLE
            )
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(codigo_sku__icontains=value) |
            Q(marca__icontains=value) |
            Q(modelo__icontains=value) |
            Q(descripcion__icontains=value)
        )


class ContratoArriendoFilter(django_filters.FilterSet):
    """
    Filtro para contratos de arriendo (administración y cliente).
    """
    estado = django_filters.ChoiceFilter(
        choices=EstadoContrato.choices,
        label='Estado del Contrato'
    )
    numero_contrato = django_filters.CharFilter(
        field_name='numero_contrato',
        lookup_expr='icontains',
        label='Número de Contrato'
    )
    fecha_desde = django_filters.DateFilter(
        field_name='creado_en__date',
        lookup_expr='gte',
        label='Fecha de Creación Desde'
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='creado_en__date',
        lookup_expr='lte',
        label='Fecha de Creación Hasta'
    )

    class Meta:
        model = ContratoArriendo
        fields = ['estado', 'numero_contrato', 'fecha_desde', 'fecha_hasta']
