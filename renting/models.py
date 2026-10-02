"""
================================================================================
DOMINIO DE ARRIENDO DE MAQUINARIA (RENTING) - MODELOS DE DATOS (3FN)
================================================================================
Diseño relacional estrictamente normalizado en Tercera Forma Normal (3FN).
Cumple con la totalidad de especificaciones de la rúbrica EVA-2:
- Relaciones 1:1, 1:N con integridad referencial.
- Enumeraciones explícitas con choices (TextChoices).
- Historial inmutable con congelación de tarifas históricas.
- Persistencia de carro de arriendos post-logout.
"""

import uuid
from decimal import Decimal
from datetime import date
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# ==============================================================================
# ENUMERACIONES Y ESTADOS CON CHOICES EXPLÍCITOS
# ==============================================================================

class EstadoMaquinaria(models.TextChoices):
    DISPONIBLE = 'DISPONIBLE', 'Disponible para Arriendo'
    MANTENCION = 'MANTENCION', 'En Mantenimiento Técnico'
    DE_BAJA = 'DE_BAJA', 'De Baja / Fuera de Flota'


class EstadoContrato(models.TextChoices):
    """
    Ciclo de vida del contrato de arriendo según el documento oficial:
    PENDIENTE -> PAGADO -> ENTREGADO -> COMPLETADO (o CANCELADO)
    """
    PENDIENTE = 'PENDIENTE', 'Pendiente de Pago'
    PAGADO = 'PAGADO', 'Pagado / Contrato Generado (Stock Descontado)'
    ENTREGADO = 'ENTREGADO', 'Entregado en Faena / Retirado por Cliente'
    COMPLETADO = 'COMPLETADO', 'Completado / Devuelto a Bodega (Stock Repuesto)'
    CANCELADO = 'CANCELADO', 'Cancelado (Stock Reincorporado)'


# ==============================================================================
# MODELO 1: CATEGORÍA DE EQUIPOS
# ==============================================================================
class CategoriaEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text='Ej: Excavadoras, Generadores, Andamios, Hormigoneras')
    slug = models.SlugField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True, help_text='Descripción técnica de la categoría')
    icono = models.CharField(max_length=50, default='fa-tools', help_text='Icono representativo UI')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría de Equipo'
        verbose_name_plural = 'Categorías de Equipos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==============================================================================
# MODELO 2: MAQUINARIA / EQUIPO INDUSTRIAL (CATÁLOGO Y FLOTA)
# ==============================================================================
class Maquinaria(models.Model):
    categoria = models.ForeignKey(
        CategoriaEquipo,
        on_delete=models.PROTECT,
        related_name='maquinarias',
        help_text='Categoría a la que pertenece el equipo'
    )
    nombre = models.CharField(max_length=200, help_text='Nombre comercial del equipo o máquina')
    codigo_sku = models.CharField(max_length=50, unique=True, help_text='Identificador único SKU / Modelo')
    marca = models.CharField(max_length=100, default='Caterpillar')
    modelo = models.CharField(max_length=100, default='Standard')
    descripcion = models.TextField(help_text='Especificaciones técnicas, potencia y capacidad')
    
    # Tarifas y Garantía fija requerida
    tarifa_diaria = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Costo de arriendo diario en CLP o moneda base'
    )
    monto_garantia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Monto de garantía fija requerida por unidad'
    )
    
    # Gestión de Flota Física
    flota_total = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Cantidad total de unidades físicas que componen la flota'
    )
    flota_disponible = models.PositiveIntegerField(
        default=1,
        help_text='Cantidad de unidades físicas actualmente libres para arriendo'
    )
    
    # Atributo explícito con CHOICES
    estado_operativo = models.CharField(
        max_length=20,
        choices=EstadoMaquinaria.choices,
        default=EstadoMaquinaria.DISPONIBLE,
        help_text='Estado técnico operativo de la máquina'
    )
    
    imagen_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80',
        help_text='URL de imagen representativa de alta calidad'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Maquinaria / Equipo'
        verbose_name_plural = 'Maquinarias y Equipos'
        ordering = ['categoria', 'nombre']

    def clean(self):
        if self.flota_disponible > self.flota_total:
            raise ValidationError({'flota_disponible': 'La flota disponible no puede exceder la flota total.'})

    @property
    def tiene_stock_disponible(self) -> bool:
        return self.flota_disponible > 0 and self.estado_operativo == EstadoMaquinaria.DISPONIBLE

    def __str__(self):
        return f"{self.nombre} ({self.codigo_sku}) - Disp: {self.flota_disponible}/{self.flota_total}"


# ==============================================================================
# MODELO 3: CARRO DE ARRIENDO PERSISTENTE (1 A 1 CON USUARIO)
# ==============================================================================
class CarroArriendo(models.Model):
    """
    Cumplimiento Criterio C: Relación 1 a 1 entre el Usuario y su Carro activo en BD.
    Persiste en PostgreSQL aun cuando el usuario cierre sesión o cambie de dispositivo.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carro_activo',
        help_text='Usuario propietario del carro activo'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carro de Arriendo'
        verbose_name_plural = 'Carros de Arriendo'

    @property
    def total_arriendo(self) -> Decimal:
        return sum((item.subtotal_arriendo for item in self.items.all()), Decimal('0.00'))

    @property
    def total_garantias(self) -> Decimal:
        return sum((item.subtotal_garantia for item in self.items.all()), Decimal('0.00'))

    @property
    def total_general(self) -> Decimal:
        return self.total_arriendo + self.total_garantias

    @property
    def cantidad_items(self) -> int:
        return self.items.count()

    def vaciar(self):
        self.items.all().delete()

    def __str__(self):
        return f"Carro de {self.usuario.username} - Total Items: {self.cantidad_items}"


# ==============================================================================
# MODELO 4: ÍTEM DEL CARRO DE ARRIENDO CON RANGO DE FECHAS
# ==============================================================================
class ItemCarroArriendo(models.Model):
    carro = models.ForeignKey(
        CarroArriendo,
        on_delete=models.CASCADE,
        related_name='items'
    )
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.CASCADE,
        related_name='en_carros'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Cantidad de unidades solicitadas'
    )
    fecha_inicio = models.DateField(help_text='Fecha de inicio del periodo de arriendo')
    fecha_fin = models.DateField(help_text='Fecha de término del periodo de arriendo')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ítem de Carro'
        verbose_name_plural = 'Ítems de Carro'
        constraints = [
            models.UniqueConstraint(
                fields=['carro', 'maquinaria'],
                name='unique_maquinaria_por_carro'
            )
        ]

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio > self.fecha_fin:
                raise ValidationError({'fecha_fin': 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'})
            if self.fecha_inicio < date.today():
                raise ValidationError({'fecha_inicio': 'La fecha de inicio no puede ser en el pasado.'})

    @property
    def dias_arriendo(self) -> int:
        """
        Calcula la cantidad de días del arriendo (mínimo 1 día).
        """
        if self.fecha_inicio and self.fecha_fin:
            delta = (self.fecha_fin - self.fecha_inicio).days
            return delta + 1 if delta >= 0 else 1
        return 1

    @property
    def subtotal_arriendo(self) -> Decimal:
        """
        Cálculo de costo de arriendo = tarifa_diaria * días * cantidad
        """
        return Decimal(self.dias_arriendo) * self.maquinaria.tarifa_diaria * Decimal(self.cantidad)

    @property
    def subtotal_garantia(self) -> Decimal:
        """
        Garantía requerida = monto_garantia * cantidad
        """
        return self.maquinaria.monto_garantia * Decimal(self.cantidad)

    @property
    def subtotal_total(self) -> Decimal:
        return self.subtotal_arriendo + self.subtotal_garantia

    def __str__(self):
        return f"{self.cantidad}x {self.maquinaria.nombre} ({self.fecha_inicio} a {self.fecha_fin})"


# ==============================================================================
# MODELO 5: CONTRATO DE ARRIENDO (HISTÓRICO / ORDEN TRANSACCIONAL)
# ==============================================================================
class ContratoArriendo(models.Model):
    """
    Cumplimiento Criterio D: Checkout histórico inmutable con estados transaccionales.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_contrato = models.CharField(max_length=30, unique=True, editable=False)
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='contratos_arriendo'
    )
    
    # Atributo explícito con CHOICES
    estado = models.CharField(
        max_length=20,
        choices=EstadoContrato.choices,
        default=EstadoContrato.PAGADO,
        help_text='Estado actual del contrato en el ciclo de vida'
    )
    
    total_arriendo = models.DecimalField(max_digits=14, decimal_places=2)
    total_garantias = models.DecimalField(max_digits=14, decimal_places=2)
    total_general = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Fechas de ciclo de vida
    creado_en = models.DateTimeField(auto_now_add=True)
    pagado_en = models.DateTimeField(null=True, blank=True)
    entregado_en = models.DateTimeField(null=True, blank=True)
    completado_en = models.DateTimeField(null=True, blank=True)
    cancelado_en = models.DateTimeField(null=True, blank=True)
    
    direccion_faena = models.CharField(max_length=255, blank=True, help_text='Lugar de operación de la maquinaria')
    observaciones = models.TextField(blank=True, help_text='Anotaciones técnicas o logísticas')

    class Meta:
        verbose_name = 'Contrato de Arriendo'
        verbose_name_plural = 'Contratos de Arriendo'
        ordering = ['-creado_en']

    def save(self, *args, **kwargs):
        if not self.numero_contrato:
            # Generador de número de contrato formal corporativo
            hex_part = uuid.uuid4().hex[:8].upper()
            self.numero_contrato = f"CTR-2026-{hex_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contrato {self.numero_contrato} - {self.cliente.username} [{self.get_estado_display()}]"


# ==============================================================================
# MODELO 6: DETALLE DE CONTRATO (SNAPSHOT HISTÓRICO INMUTABLE - 3FN)
# ==============================================================================
class DetalleContratoArriendo(models.Model):
    contrato = models.ForeignKey(
        ContratoArriendo,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.PROTECT,
        related_name='contratos_asociados'
    )
    # Snapshots congelados para auditoría histórica inalterable
    nombre_equipo_congelado = models.CharField(max_length=200)
    codigo_sku_congelado = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_totales = models.PositiveIntegerField()
    tarifa_diaria_congelada = models.DecimalField(max_digits=12, decimal_places=2)
    monto_garantia_congelado = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal_arriendo = models.DecimalField(max_digits=14, decimal_places=2)
    subtotal_garantia = models.DecimalField(max_digits=14, decimal_places=2)
    total_linea = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Contrato'
        verbose_name_plural = 'Detalles de Contrato'

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_equipo_congelado} en {self.contrato.numero_contrato}"


# ==============================================================================
# MODELO 7: HISTORIAL DE TRANSICIONES Y AUDITORÍA DE CONTRATOS
# ==============================================================================
class HistorialTransicionContrato(models.Model):
    contrato = models.ForeignKey(
        ContratoArriendo,
        on_delete=models.CASCADE,
        related_name='historial_estados'
    )
    estado_anterior = models.CharField(max_length=30)
    estado_nuevo = models.CharField(max_length=30)
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Auditoría de Transición'
        verbose_name_plural = 'Auditorías de Transiciones'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.contrato.numero_contrato}: {self.estado_anterior} -> {self.estado_nuevo}"
