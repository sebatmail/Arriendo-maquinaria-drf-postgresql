"""
================================================================================
SERIALIZADORES DRF PARA RENTING DE MAQUINARIA (EVA-2)
================================================================================
Serializadores de alto rendimiento con validaciones de fechas, cálculo dinámico
de garantías y tarifas diarias, y snapshots inmutables para contratos.
"""

from decimal import Decimal
from datetime import date
from rest_framework import serializers
from django.db import transaction
from .models import (
    CategoriaEquipo,
    Maquinaria,
    CarroArriendo,
    ItemCarroArriendo,
    ContratoArriendo,
    DetalleContratoArriendo,
    HistorialTransicionContrato,
    EstadoContrato,
    EstadoMaquinaria
)
from authentication.serializers import UsuarioSerializer

# ==============================================================================
# SERIALIZADOR DE CATEGORÍAS
# ==============================================================================
class CategoriaEquipoSerializer(serializers.ModelSerializer):
    total_maquinarias = serializers.IntegerField(source='maquinarias.count', read_only=True)

    class Meta:
        model = CategoriaEquipo
        fields = ['id', 'nombre', 'slug', 'descripcion', 'icono', 'total_maquinarias', 'creado_en']
        read_only_fields = ['id', 'creado_en', 'total_maquinarias']


# ==============================================================================
# SERIALIZADOR DE MAQUINARIA (CATÁLOGO Y FLOTA)
# ==============================================================================
class MaquinariaSerializer(serializers.ModelSerializer):
    categoria_detalle = CategoriaEquipoSerializer(source='categoria', read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaEquipo.objects.all(),
        source='categoria',
        write_only=True
    )
    estado_operativo_display = serializers.CharField(source='get_estado_operativo_display', read_only=True)
    tiene_stock_disponible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Maquinaria
        fields = [
            'id',
            'categoria_id',
            'categoria_detalle',
            'nombre',
            'codigo_sku',
            'marca',
            'modelo',
            'descripcion',
            'tarifa_diaria',
            'monto_garantia',
            'flota_total',
            'flota_disponible',
            'estado_operativo',
            'estado_operativo_display',
            'tiene_stock_disponible',
            'imagen_url',
            'creado_en',
            'actualizado_en'
        ]
        read_only_fields = [
            'id',
            'creado_en',
            'actualizado_en',
            'estado_operativo_display',
            'tiene_stock_disponible'
        ]

    def validate(self, attrs):
        flota_total = attrs.get('flota_total')
        flota_disponible = attrs.get('flota_disponible')
        
        if self.instance:
            flota_total = flota_total or self.instance.flota_total
            flota_disponible = flota_disponible if flota_disponible is not None else self.instance.flota_disponible

        if flota_disponible is not None and flota_total is not None:
            if flota_disponible > flota_total:
                raise serializers.ValidationError({
                    'flota_disponible': 'La flota disponible no puede ser mayor que la flota total del inventario.'
                })
        return attrs


# ==============================================================================
# SERIALIZADORES DEL CARRO DE ARRIENDO (PERSISTENTE)
# ==============================================================================
class ItemCarroArriendoSerializer(serializers.ModelSerializer):
    maquinaria_detalle = MaquinariaSerializer(source='maquinaria', read_only=True)
    dias_arriendo = serializers.IntegerField(read_only=True)
    subtotal_arriendo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    subtotal_garantia = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    subtotal_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarroArriendo
        fields = [
            'id',
            'maquinaria',
            'maquinaria_detalle',
            'cantidad',
            'fecha_inicio',
            'fecha_fin',
            'dias_arriendo',
            'subtotal_arriendo',
            'subtotal_garantia',
            'subtotal_total',
            'creado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'dias_arriendo', 'subtotal_arriendo', 'subtotal_garantia', 'subtotal_total']


class AgregarItemCarroSerializer(serializers.Serializer):
    """
    Serializador para agregar o modificar ítems en el carro de arriendo.
    Valida fechas coherentes, disponibilidad de catálogo y cantidad solicitada.
    """
    maquinaria_id = serializers.PrimaryKeyRelatedField(
        queryset=Maquinaria.objects.all(),
        source='maquinaria'
    )
    cantidad = serializers.IntegerField(min_value=1, default=1)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()

    def validate(self, attrs):
        fecha_inicio = attrs['fecha_inicio']
        fecha_fin = attrs['fecha_fin']
        maquinaria = attrs['maquinaria']
        cantidad = attrs['cantidad']

        hoy = date.today()
        if fecha_inicio < hoy:
            raise serializers.ValidationError({'fecha_inicio': 'La fecha de inicio no puede ser anterior a hoy.'})
        
        if fecha_fin < fecha_inicio:
            raise serializers.ValidationError({'fecha_fin': 'La fecha de fin debe ser igual o posterior a la fecha de inicio.'})

        if maquinaria.estado_operativo != EstadoMaquinaria.DISPONIBLE:
            raise serializers.ValidationError({'maquinaria_id': f'El equipo {maquinaria.nombre} no se encuentra disponible operativamente.'})

        return attrs


class CarroArriendoSerializer(serializers.ModelSerializer):
    items = ItemCarroArriendoSerializer(many=True, read_only=True)
    total_arriendo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_garantias = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_general = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = CarroArriendo
        fields = [
            'id',
            'usuario',
            'items',
            'cantidad_items',
            'total_arriendo',
            'total_garantias',
            'total_general',
            'actualizado_en'
        ]
        read_only_fields = ['id', 'usuario', 'actualizado_en']


# ==============================================================================
# SERIALIZADORES DE CONTRATOS Y HISTORIAL DE ESTADOS
# ==============================================================================
class DetalleContratoArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleContratoArriendo
        fields = [
            'id',
            'maquinaria',
            'nombre_equipo_congelado',
            'codigo_sku_congelado',
            'cantidad',
            'fecha_inicio',
            'fecha_fin',
            'dias_totales',
            'tarifa_diaria_congelada',
            'monto_garantia_congelado',
            'subtotal_arriendo',
            'subtotal_garantia',
            'total_linea'
        ]


class HistorialTransicionContratoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='cambiado_por.get_full_name', read_only=True)

    class Meta:
        model = HistorialTransicionContrato
        fields = [
            'id',
            'estado_anterior',
            'estado_nuevo',
            'cambiado_por',
            'usuario_nombre',
            'fecha_registro',
            'comentarios'
        ]


class ContratoArriendoSerializer(serializers.ModelSerializer):
    detalles = DetalleContratoArriendoSerializer(many=True, read_only=True)
    historial_estados = HistorialTransicionContratoSerializer(many=True, read_only=True)
    cliente_detalle = UsuarioSerializer(source='cliente', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ContratoArriendo
        fields = [
            'id',
            'numero_contrato',
            'cliente',
            'cliente_detalle',
            'estado',
            'estado_display',
            'total_arriendo',
            'total_garantias',
            'total_general',
            'direccion_faena',
            'observaciones',
            'creado_en',
            'pagado_en',
            'entregado_en',
            'completado_en',
            'cancelado_en',
            'detalles',
            'historial_estados'
        ]
        read_only_fields = [
            'id', 'numero_contrato', 'cliente', 'estado', 'estado_display',
            'total_arriendo', 'total_garantias', 'total_general', 'creado_en',
            'pagado_en', 'entregado_en', 'completado_en', 'cancelado_en'
        ]


class CheckoutContratoSerializer(serializers.Serializer):
    """
    Datos de entrada para confirmar el arriendo y generar la orden.
    """
    direccion_faena = serializers.CharField(max_length=255, required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)


class ActualizarEstadoContratoSerializer(serializers.Serializer):
    """
    Permite al Ejecutivo de Arriendos realizar la transición de estados:
    - ENTREGADO: Al despachar/retirar equipo
    - COMPLETADO: Al devolver equipo a bodega (repone flota_disponible)
    - CANCELADO: Si se anula la operación (repone flota_disponible)
    """
    nuevo_estado = serializers.ChoiceField(choices=EstadoContrato.choices)
    comentarios = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_nuevo_estado(self, value):
        contrato = self.context.get('contrato')
        if not contrato:
            return value

        estado_actual = contrato.estado
        
        # Validaciones de transiciones de negocio
        if estado_actual == EstadoContrato.COMPLETADO:
            raise serializers.ValidationError("Un contrato COMPLETADO es un registro histórico final y no puede cambiar de estado.")
        
        if estado_actual == EstadoContrato.CANCELADO:
            raise serializers.ValidationError("Un contrato CANCELADO no puede ser reactivado.")

        if value == estado_actual:
            raise serializers.ValidationError(f"El contrato ya se encuentra en estado {estado_actual}.")

        return value
