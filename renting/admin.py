"""
================================================================================
ADMINISTRACIÓN DJANGO ADMIN - DOMINIO DE RENTING
================================================================================
"""

from django.contrib import admin
from .models import (
    CategoriaEquipo,
    Maquinaria,
    CarroArriendo,
    ItemCarroArriendo,
    ContratoArriendo,
    DetalleContratoArriendo,
    HistorialTransicionContrato
)

class DetalleContratoInline(admin.TabularInline):
    model = DetalleContratoArriendo
    extra = 0
    readonly_fields = [
        'maquinaria', 'nombre_equipo_congelado', 'codigo_sku_congelado',
        'cantidad', 'fecha_inicio', 'fecha_fin', 'dias_totales',
        'tarifa_diaria_congelada', 'monto_garantia_congelado',
        'subtotal_arriendo', 'subtotal_garantia', 'total_linea'
    ]
    can_delete = False


class HistorialTransicionInline(admin.TabularInline):
    model = HistorialTransicionContrato
    extra = 0
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha_registro', 'comentarios']
    can_delete = False


class ItemCarroInline(admin.TabularInline):
    model = ItemCarroArriendo
    extra = 0


@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'icono', 'creado_en']
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre', 'descripcion']


@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'codigo_sku', 'categoria', 'tarifa_diaria',
        'monto_garantia', 'flota_disponible', 'flota_total',
        'estado_operativo', 'creado_en'
    ]
    list_filter = ['categoria', 'estado_operativo', 'marca']
    search_fields = ['nombre', 'codigo_sku', 'marca', 'modelo', 'descripcion']
    list_editable = ['tarifa_diaria', 'monto_garantia', 'flota_disponible', 'estado_operativo']


@admin.register(CarroArriendo)
class CarroArriendoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cantidad_items', 'total_arriendo', 'total_garantias', 'total_general', 'actualizado_en']
    inlines = [ItemCarroInline]
    search_fields = ['usuario__username', 'usuario__email', 'usuario__razon_social']


@admin.register(ContratoArriendo)
class ContratoArriendoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_contrato', 'cliente', 'estado', 'total_arriendo',
        'total_garantias', 'total_general', 'creado_en', 'pagado_en'
    ]
    list_filter = ['estado', 'creado_en']
    search_fields = ['numero_contrato', 'cliente__username', 'cliente__razon_social', 'cliente__rut_empresa']
    inlines = [DetalleContratoInline, HistorialTransicionInline]
    readonly_fields = ['id', 'numero_contrato', 'creado_en', 'pagado_en', 'entregado_en', 'completado_en', 'cancelado_en']
