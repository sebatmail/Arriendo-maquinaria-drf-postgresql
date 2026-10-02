"""
================================================================================
RUTAS DE LA API DE RENTING DE MAQUINARIA (DRF)
================================================================================
Cumple con la matriz exacta de endpoints y permisos especificados en la pauta EVA-2.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaEquipoViewSet,
    MaquinariaViewSet,
    CarroArriendoView,
    EliminarItemCarroView,
    CheckoutContratoView,
    MisContratosListView,
    MiContratoDetailView,
    AdminContratosListView,
    AdminActualizarEstadoContratoView
)

router = DefaultRouter()
router.register(r'categorias', CategoriaEquipoViewSet, basename='categoria')
router.register(r'maquinarias', MaquinariaViewSet, basename='maquinaria')

urlpatterns = [
    # Rutas automáticas del router (Catálogo público y CRUD ejecutivo)
    path('', include(router.urls)),

    # Rutas de Carro de Arriendo (Empresa Constructora)
    path('carro-arriendo/', CarroArriendoView.as_view(), name='carro_arriendo'),
    path('carro-arriendo/items/<int:item_id>/', EliminarItemCarroView.as_view(), name='eliminar_item_carro'),

    # Rutas de Contratos y Checkout (Empresa Constructora)
    path('contratos/checkout/', CheckoutContratoView.as_view(), name='contratos_checkout'),
    path('mis-contratos/', MisContratosListView.as_view(), name='mis_contratos_list'),
    path('mis-contratos/<uuid:pk>/', MiContratoDetailView.as_view(), name='mis_contratos_detail'),

    # Rutas de Administración de Contratos (Ejecutivo de Arriendos)
    path('contratos/', AdminContratosListView.as_view(), name='admin_contratos_list'),
    path('contratos/<uuid:pk>/estado/', AdminActualizarEstadoContratoView.as_view(), name='admin_actualizar_estado_contrato'),
]
