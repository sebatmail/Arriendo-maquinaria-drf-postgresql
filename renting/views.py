"""
================================================================================
CONTROLADORES Y VISTAS DE API REST (DRF) - RENTING DE MAQUINARIA
================================================================================
Implementa la lógica transaccional de negocio con concurrencia atómica,
reserva de inventario en estado PAGADO, reposición en COMPLETADO/CANCELADO,
y matriz RBAC estricta según la pauta EVA-2.
"""

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

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
from .serializers import (
    CategoriaEquipoSerializer,
    MaquinariaSerializer,
    CarroArriendoSerializer,
    ItemCarroArriendoSerializer,
    AgregarItemCarroSerializer,
    ContratoArriendoSerializer,
    CheckoutContratoSerializer,
    ActualizarEstadoContratoSerializer
)
from .filters import MaquinariaFilter, ContratoArriendoFilter
from authentication.permissions import (
    IsEmpresaConstructora,
    IsEjecutivoArriendos,
    IsAdminOrReadOnly
)

# ==============================================================================
# VISTA PÚBLICA / ADMIN: CATEGORÍAS DE EQUIPOS
# ==============================================================================
@extend_schema(tags=['Catálogo y Maquinarias'])
class CategoriaEquipoViewSet(viewsets.ModelViewSet):
    """
    CRUD de Categorías. Lectura pública, mutaciones exclusivas para Ejecutivos.
    """
    queryset = CategoriaEquipo.objects.all()
    serializer_class = CategoriaEquipoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creado_en']


# ==============================================================================
# VISTA PÚBLICA / ADMIN: CATÁLOGO Y GESTIÓN DE MAQUINARIAS
# ==============================================================================
@extend_schema(tags=['Catálogo y Maquinarias'])
class MaquinariaViewSet(viewsets.ModelViewSet):
    """
    Gestión de Maquinaria y Equipos Industriales.
    - Público: GET /api/maquinarias/ (con filtrado avanzado django-filter)
    - Ejecutivo de Arriendos: POST / PUT / PATCH / DELETE
    """
    queryset = Maquinaria.objects.select_related('categoria').all()
    serializer_class = MaquinariaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = MaquinariaFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'codigo_sku', 'marca', 'modelo', 'descripcion']
    ordering_fields = ['tarifa_diaria', 'flota_disponible', 'creado_en', 'nombre']
    ordering = ['categoria', 'nombre']


# ==============================================================================
# VISTAS DE EMPRESA CONSTRUCTORA: CARRO DE ARRIENDO PERSISTENTE
# ==============================================================================
@extend_schema(tags=['Carro de Arriendo (Empresa Constructora)'])
class CarroArriendoView(APIView):
    """
    Gestiona el carro de arriendo persistente en base de datos PostgreSQL (1 a 1 con Usuario).
    Conserva los ítems tras cerrar sesión (logout) o cambiar de dispositivo.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmpresaConstructora]

    def get_or_create_carro(self, user):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=user)
        return carro

    @extend_schema(
        summary='Consultar Carro de Arriendo Activo',
        description='Obtiene los ítems persistidos en el carro del usuario autenticado con cálculo en vivo de totales.',
        responses={200: CarroArriendoSerializer}
    )
    def get(self, request):
        carro = self.get_or_create_carro(request.user)
        serializer = CarroArriendoSerializer(carro)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Agregar o Actualizar Ítem en el Carro',
        description='Agrega una maquinaria al carro con sus fechas de inicio y fin, o actualiza su cantidad si ya existe.',
        request=AgregarItemCarroSerializer,
        responses={201: CarroArriendoSerializer}
    )
    def post(self, request):
        carro = self.get_or_create_carro(request.user)
        serializer = AgregarItemCarroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maquinaria = serializer.validated_data['maquinaria']
        cantidad = serializer.validated_data['cantidad']
        fecha_inicio = serializer.validated_data['fecha_inicio']
        fecha_fin = serializer.validated_data['fecha_fin']

        # Verificación preliminar de stock en catálogo
        if maquinaria.flota_disponible < cantidad:
            return Response(
                {
                    'error': f'Stock insuficiente. La máquina {maquinaria.nombre} solo dispone de {maquinaria.flota_disponible} unidad(es) libre(s).'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualiza o crea el ítem en PostgreSQL
        item, created = ItemCarroArriendo.objects.update_or_create(
            carro=carro,
            maquinaria=maquinaria,
            defaults={
                'cantidad': cantidad,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        )

        carro_serializado = CarroArriendoSerializer(carro).data
        return Response(
            {
                'mensaje': 'Equipo agregado al carro de arriendo exitosamente.',
                'item_id': item.id,
                'carro': carro_serializado
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(
        summary='Vaciar Carro de Arriendo',
        description='Elimina todos los ítems contenidos en el carro activo del usuario.',
        responses={200: OpenApiResponse(description='Carro vaciado exitosamente')}
    )
    def delete(self, request):
        carro = self.get_or_create_carro(request.user)
        carro.vaciar()
        return Response({'mensaje': 'El carro de arriendo ha sido vaciado por completo.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Carro de Arriendo (Empresa Constructora)'])
class EliminarItemCarroView(APIView):
    """
    Elimina un ítem específico del carro de arriendo persistente.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmpresaConstructora]

    @extend_schema(
        summary='Eliminar Ítem del Carro',
        description='Remueve una maquinaria específica del carro de compras.',
        responses={200: OpenApiResponse(description='Ítem removido con éxito')}
    )
    def delete(self, request, item_id):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        try:
            item = ItemCarroArriendo.objects.get(id=item_id, carro=carro)
            item.delete()
            return Response(
                {
                    'mensaje': 'Ítem eliminado del carro con éxito.',
                    'carro': CarroArriendoSerializer(carro).data
                },
                status=status.HTTP_200_OK
            )
        except ItemCarroArriendo.DoesNotExist:
            return Response({'error': 'El ítem indicado no existe en su carro de arriendo.'}, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# VISTA TRANSACCIONAL ATÓMICA: CHECKOUT Y CREACIÓN DE CONTRATO (CRITERIO D)
# ==============================================================================
@extend_schema(tags=['Contratos y Checkout (Empresa Constructora)'])
class CheckoutContratoView(APIView):
    """
    Lógica de Checkout y Descuento Atómico de Inventario:
    1. Ejecuta dentro de un bloque atómico de transacción (`transaction.atomic()`).
    2. Bloquea filas mediante `select_for_update()` para evitar condiciones de carrera (Race Conditions).
    3. Valida que cada maquinaria disponga de unidades libres suficientes.
    4. Si hay stock: descuenta la flota disponible, genera el Contrato de Arriendo inmutable (PAGADO),
       crea los snapshots de detalle, registra la auditoría y liquida el carro persistente.
    5. Si el stock es insuficiente: revierte la transacción íntegra y rechaza con 400 Bad Request.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmpresaConstructora]

    @extend_schema(
        summary='Confirmar Arriendo y Checkout Transaccional',
        description='Liquida el carro activo, valida stock con bloqueo atómico, descuenta flota y genera el Contrato de Arriendo PAGADO.',
        request=CheckoutContratoSerializer,
        responses={201: ContratoArriendoSerializer}
    )
    def post(self, request):
        serializer = CheckoutContratoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        direccion_faena = serializer.validated_data.get('direccion_faena', '') or request.user.direccion_obra or ''
        observaciones = serializer.validated_data.get('observaciones', '')

        user = request.user
        carro, _ = CarroArriendo.objects.get_or_create(usuario=user)
        items_carro = list(carro.items.select_related('maquinaria').all())

        if not items_carro:
            return Response(
                {'error': 'No es posible procesar el arriendo: el carro se encuentra vacío.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Obtención de IDs de maquinarias involucradas
                maquinarias_ids = [item.maquinaria.id for item in items_carro]
                
                # Bloqueo pesimista en PostgreSQL para control de concurrencia
                maquinarias_bloqueadas = {
                    m.id: m for m in Maquinaria.objects.select_for_update().filter(id__in=maquinarias_ids)
                }

                # 1. Validación estricta de disponibilidad física
                for item in items_carro:
                    maq = maquinarias_bloqueadas.get(item.maquinaria.id)
                    if not maq:
                        raise ValueError(f"La máquina ID {item.maquinaria.id} no existe en el inventario.")

                    if maq.estado_operativo != EstadoMaquinaria.DISPONIBLE:
                        raise ValueError(
                            f"La maquinaria '{maq.nombre}' está en estado '{maq.get_estado_operativo_display()}' y no puede ser arrendada."
                        )

                    if maq.flota_disponible < item.cantidad:
                        raise ValueError(
                            f"Inventario insuficiente para '{maq.nombre}'. Solicitadas: {item.cantidad}, Disponibles en flota: {maq.flota_disponible}."
                        )

                # 2. Cálculo consolidado y descuento de flota
                total_arriendo_acum = Decimal('0.00')
                total_garantias_acum = Decimal('0.00')

                for item in items_carro:
                    maq = maquinarias_bloqueadas[item.maquinaria.id]
                    # Descuento atómico en base de datos
                    maq.flota_disponible -= item.cantidad
                    maq.save(update_fields=['flota_disponible'])

                    total_arriendo_acum += item.subtotal_arriendo
                    total_garantias_acum += item.subtotal_garantia

                total_general_acum = total_arriendo_acum + total_garantias_acum
                ahora = timezone.now()

                # 3. Creación del Contrato Histórico (PAGADO)
                contrato = ContratoArriendo.objects.create(
                    cliente=user,
                    estado=EstadoContrato.PAGADO,
                    total_arriendo=total_arriendo_acum,
                    total_garantias=total_garantias_acum,
                    total_general=total_general_acum,
                    pagado_en=ahora,
                    direccion_faena=direccion_faena,
                    observaciones=observaciones
                )

                # 4. Creación de Snapshots inmutables de Detalle (3FN)
                for item in items_carro:
                    maq = maquinarias_bloqueadas[item.maquinaria.id]
                    DetalleContratoArriendo.objects.create(
                        contrato=contrato,
                        maquinaria=maq,
                        nombre_equipo_congelado=maq.nombre,
                        codigo_sku_congelado=maq.codigo_sku,
                        cantidad=item.cantidad,
                        fecha_inicio=item.fecha_inicio,
                        fecha_fin=item.fecha_fin,
                        dias_totales=item.dias_arriendo,
                        tarifa_diaria_congelada=maq.tarifa_diaria,
                        monto_garantia_congelado=maq.monto_garantia,
                        subtotal_arriendo=item.subtotal_arriendo,
                        subtotal_garantia=item.subtotal_garantia,
                        total_linea=item.subtotal_total
                    )

                # 5. Registro de Auditoría de Transición
                HistorialTransicionContrato.objects.create(
                    contrato=contrato,
                    estado_anterior='INICIAL (CARRO)',
                    estado_nuevo=EstadoContrato.PAGADO,
                    cambiado_por=user,
                    comentarios='Checkout exitoso. Pago confirmado y descuento de flota aplicado.'
                )

                # 6. Liquidación del Carro Persistente
                carro.vaciar()

            # Respuesta serializada completa
            return Response(
                {
                    'mensaje': 'Contrato de Arriendo confirmado y pagado exitosamente. Flota descontada.',
                    'contrato': ContratoArriendoSerializer(contrato).data
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Error interno durante el procesamiento transaccional: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==============================================================================
# VISTA DE HISTORIAL DE CONTRATOS (CLIENTE)
# ==============================================================================
@extend_schema(tags=['Contratos y Checkout (Empresa Constructora)'])
class MisContratosListView(generics.ListAPIView):
    """
    Listado histórico de todos los contratos de arriendo pertenecientes a la Empresa Constructora autenticada.
    """
    serializer_class = ContratoArriendoSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmpresaConstructora]
    filterset_class = ContratoArriendoFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['creado_en', 'total_general', 'estado']
    ordering = ['-creado_en']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return ContratoArriendo.objects.none()
        return ContratoArriendo.objects.filter(cliente=self.request.user).prefetch_related('detalles', 'historial_estados')


@extend_schema(tags=['Contratos y Checkout (Empresa Constructora)'])
class MiContratoDetailView(generics.RetrieveAPIView):
    """
    Detalle completo de un contrato específico de la Empresa Constructora autenticada.
    """
    serializer_class = ContratoArriendoSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmpresaConstructora]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return ContratoArriendo.objects.none()
        return ContratoArriendo.objects.filter(cliente=self.request.user).prefetch_related('detalles', 'historial_estados')


# ==============================================================================
# VISTAS DE EJECUTIVO DE ARRIENDOS (ADMINISTRACIÓN GENERAL DE CONTRATOS)
# ==============================================================================
@extend_schema(tags=['Administración de Contratos (Ejecutivo de Arriendos)'])
class AdminContratosListView(generics.ListAPIView):
    """
    Permite al Ejecutivo de Arriendos supervisar y filtrar la totalidad de contratos del sistema.
    """
    queryset = ContratoArriendo.objects.select_related('cliente').prefetch_related('detalles', 'historial_estados').all()
    serializer_class = ContratoArriendoSerializer
    permission_classes = [permissions.IsAuthenticated, IsEjecutivoArriendos]
    filterset_class = ContratoArriendoFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['numero_contrato', 'cliente__username', 'cliente__razon_social', 'cliente__rut_empresa']
    ordering_fields = ['creado_en', 'total_general', 'estado']
    ordering = ['-creado_en']


@extend_schema(tags=['Administración de Contratos (Ejecutivo de Arriendos)'])
class AdminActualizarEstadoContratoView(APIView):
    """
    Transición de Estados con Control de Reposición de Flota:
    - ENTREGADO: Al retirar la máquina de bodega o despachar a obra.
    - COMPLETADO: Al devolver el equipo a bodega. Repone automáticamente la flota al inventario disponible.
    - CANCELADO: En caso de anulación. Reincorpora automáticamente la flota al catálogo.
    """
    permission_classes = [permissions.IsAuthenticated, IsEjecutivoArriendos]

    @extend_schema(
        summary='Actualizar Estado de Contrato (Transición RBAC)',
        description='Cambia el estado de un contrato (ENTREGADO, COMPLETADO, CANCELADO) y gestiona la reposición automática de stock.',
        request=ActualizarEstadoContratoSerializer,
        responses={200: ContratoArriendoSerializer}
    )
    def patch(self, request, pk):
        try:
            contrato = ContratoArriendo.objects.prefetch_related('detalles__maquinaria').get(pk=pk)
        except ContratoArriendo.DoesNotExist:
            return Response({'error': 'Contrato de arriendo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ActualizarEstadoContratoSerializer(data=request.data, context={'contrato': contrato})
        serializer.is_valid(raise_exception=True)

        nuevo_estado = serializer.validated_data['nuevo_estado']
        comentarios = serializer.validated_data.get('comentarios', '')
        estado_anterior = contrato.estado
        ahora = timezone.now()

        with transaction.atomic():
            # Casos especiales de reposición de flota: COMPLETADO o CANCELADO
            if nuevo_estado in [EstadoContrato.COMPLETADO, EstadoContrato.CANCELADO]:
                for detalle in contrato.detalles.all():
                    # Bloqueo pesimista para actualización segura
                    maq = Maquinaria.objects.select_for_update().get(id=detalle.maquinaria.id)
                    # Reposición de unidades (sin superar flota total)
                    maq.flota_disponible = min(maq.flota_total, maq.flota_disponible + detalle.cantidad)
                    maq.save(update_fields=['flota_disponible'])

            # Asignación de timestamps según estado
            if nuevo_estado == EstadoContrato.ENTREGADO:
                contrato.entregado_en = ahora
            elif nuevo_estado == EstadoContrato.COMPLETADO:
                contrato.completado_en = ahora
            elif nuevo_estado == EstadoContrato.CANCELADO:
                contrato.cancelado_en = ahora
            elif nuevo_estado == EstadoContrato.PAGADO and not contrato.pagado_en:
                contrato.pagado_en = ahora

            contrato.estado = nuevo_estado
            contrato.save()

            # Auditoría histórica inmutable
            HistorialTransicionContrato.objects.create(
                contrato=contrato,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                cambiado_por=request.user,
                comentarios=comentarios or f'Estado actualizado por {request.user.get_full_name() or request.user.username}'
            )

        return Response(
            {
                'mensaje': f'Estado del contrato {contrato.numero_contrato} actualizado a {contrato.get_estado_display()}.',
                'contrato': ContratoArriendoSerializer(contrato).data
            },
            status=status.HTTP_200_OK
        )
