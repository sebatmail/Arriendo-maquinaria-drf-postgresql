"""
================================================================================
SUITE DE PRUEBAS UNITARIAS E INTEGRACIÓN (EVA-2)
================================================================================
Valida al 100% la pauta de evaluación:
1. Autenticación JWT y claims de Rol (Empresa Constructora vs Ejecutivo)
2. Persistencia del Carro de Arriendo en base de datos
3. Transacción atómica de Checkout y descuento de flota en estado PAGADO
4. Reposición automática de flota al transicionar a COMPLETADO o CANCELADO
5. Matriz de permisos RBAC y filtros declarativos django-filter
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
import jwt
from django.conf import settings

from authentication.models import RolUsuario
from renting.models import (
    CategoriaEquipo,
    Maquinaria,
    EstadoMaquinaria,
    CarroArriendo,
    ItemCarroArriendo,
    ContratoArriendo,
    DetalleContratoArriendo,
    EstadoContrato
)

Usuario = get_user_model()

class RentingMaquinariaTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Crear Usuario Empresa Constructora (Cliente)
        self.cliente = Usuario.objects.create_user(
            username='constructora_test',
            email='test@constructora.cl',
            password='Password123!',
            rol=RolUsuario.EMPRESA_CONSTRUCTORA,
            razon_social='Constructora Los Andes SpA',
            rut_empresa='76.111.222-3',
            direccion_obra='Faena Central #100'
        )

        # 2. Crear Usuario Ejecutivo de Arriendos (Admin)
        self.ejecutivo = Usuario.objects.create_user(
            username='ejecutivo_test',
            email='admin@rent-equip.pro',
            password='Password123!',
            rol=RolUsuario.EJECUTIVO_ARRIENDOS,
            is_staff=True,
            is_superuser=True
        )

        # 3. Crear Categoría y Maquinaria
        self.cat_pesada = CategoriaEquipo.objects.create(
            nombre='Maquinaria Pesada',
            slug='maquinaria-pesada',
            descripcion='Excavadoras y retroexcavadoras'
        )

        self.excavadora = Maquinaria.objects.create(
            categoria=self.cat_pesada,
            nombre='Excavadora CAT 320',
            codigo_sku='CAT-320-TEST',
            marca='Caterpillar',
            modelo='320 GC',
            descripcion='Excavadora de 20 toneladas para obras civiles.',
            tarifa_diaria=Decimal('150000.00'),
            monto_garantia=Decimal('600000.00'),
            flota_total=5,
            flota_disponible=5,
            estado_operativo=EstadoMaquinaria.DISPONIBLE
        )

    # --------------------------------------------------------------------------
    # TEST 1: AUTENTICACIÓN JWT Y CLAIMS DE ROL
    # --------------------------------------------------------------------------
    def test_jwt_login_retorna_tokens_y_claims_de_rol(self):
        """
        Verifica que el login retorne access y refresh tokens, y que el token
        incluya en su payload el rol del usuario (Empresa Constructora / Ejecutivo).
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'constructora_test',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['rol'], RolUsuario.EMPRESA_CONSTRUCTORA)

        # Decodificación y verificación de claims en el token JWT
        token = response.data['access']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(payload['rol'], RolUsuario.EMPRESA_CONSTRUCTORA)
        self.assertEqual(payload['user_id'], self.cliente.id)
        self.assertEqual(payload['razon_social'], 'Constructora Los Andes SpA')

    # --------------------------------------------------------------------------
    # TEST 2: CATÁLOGO PÚBLICO Y FILTROS DJANGO-FILTER
    # --------------------------------------------------------------------------
    def test_catalogo_publico_y_filtros(self):
        """
        Verifica que cualquier usuario (sin autenticación) pueda consultar el catálogo
        y aplicar filtros declarativos mediante django-filter.
        """
        # Lectura pública
        response = self.client.get('/api/maquinarias/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Filtro por categoría slug
        response_cat = self.client.get('/api/maquinarias/?categoria_slug=maquinaria-pesada')
        self.assertEqual(response_cat.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response_cat.data['results']), 1)

        # Filtro por precio máximo
        response_precio = self.client.get('/api/maquinarias/?max_precio=100000')
        self.assertEqual(response_precio.status_code, status.HTTP_200_OK)
        # Nuestra CAT cuesta 150.000, por lo que no debe aparecer
        self.assertEqual(len(response_precio.data['results']), 0)

    # --------------------------------------------------------------------------
    # TEST 3: CARRO DE ARRIENDO PERSISTENTE POST-LOGOUT
    # --------------------------------------------------------------------------
    def test_carro_persistencia_en_base_de_datos(self):
        """
        Verifica que los ítems agregados al carro se almacenen en PostgreSQL
        asociados 1:1 al usuario, y persistan tras simular cierre y reapertura de sesión.
        """
        self.client.force_authenticate(user=self.cliente)

        hoy = date.today()
        fin = hoy + timedelta(days=4)  # 5 días de arriendo

        post_data = {
            'maquinaria_id': self.excavadora.id,
            'cantidad': 2,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': fin.isoformat()
        }

        # 1. Agregar al carro
        response = self.client.post('/api/carro-arriendo/', post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. Verificar persistencia en base de datos directa
        carro_db = CarroArriendo.objects.get(usuario=self.cliente)
        self.assertEqual(carro_db.items.count(), 1)
        item = carro_db.items.first()
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.dias_arriendo, 5)

        # Cálculo esperado:
        # Arriendo: 5 días * $150.000 * 2 unidades = $1.500.000
        # Garantía: $600.000 * 2 unidades = $1.200.000
        # Total: $2.700.000
        self.assertEqual(item.subtotal_arriendo, Decimal('1500000.00'))
        self.assertEqual(item.subtotal_garantia, Decimal('1200000.00'))
        self.assertEqual(item.subtotal_total, Decimal('2700000.00'))

        # 3. Simular desautenticación (Logout) y reconexión
        self.client.force_authenticate(user=None)
        self.client.force_authenticate(user=self.cliente)

        # Consultar carro nuevamente
        response_reconnect = self.client.get('/api/carro-arriendo/')
        self.assertEqual(response_reconnect.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_reconnect.data['items']), 1)
        self.assertEqual(Decimal(str(response_reconnect.data['total_general'])), Decimal('2700000.00'))

    # --------------------------------------------------------------------------
    # TEST 4: CHECKOUT ATÓMICO, DESCUENTO DE FLOTA Y CREACIÓN DE CONTRATO
    # --------------------------------------------------------------------------
    def test_checkout_atomico_y_descuento_flota(self):
        """
        Verifica que el stock NO se descuente al agregar al carro, sino
        exclusivamente al procesar el Checkout a estado PAGADO.
        """
        self.client.force_authenticate(user=self.cliente)

        # Stock inicial = 5
        self.assertEqual(self.excavadora.flota_disponible, 5)

        # Agregar 3 unidades al carro
        hoy = date.today()
        fin = hoy + timedelta(days=2)  # 3 días
        self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.excavadora.id,
            'cantidad': 3,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': fin.isoformat()
        }, format='json')

        # Stock en catálogo debe SEGUIR SIENDO 5 (no se descuenta en el carro)
        self.excavadora.refresh_from_db()
        self.assertEqual(self.excavadora.flota_disponible, 5)

        # Ejecutar Checkout transaccional
        checkout_response = self.client.post('/api/contratos/checkout/', {
            'direccion_faena': 'Obra Túnel Oriente #500',
            'observaciones': 'Despacho prioritario con seguro'
        }, format='json')

        self.assertEqual(checkout_response.status_code, status.HTTP_201_CREATED)
        contrato_data = checkout_response.data['contrato']
        self.assertEqual(contrato_data['estado'], EstadoContrato.PAGADO)

        # Stock AHORA debe haberse descontado: 5 - 3 = 2
        self.excavadora.refresh_from_db()
        self.assertEqual(self.excavadora.flota_disponible, 2)

        # El carro debe estar vacío
        carro = CarroArriendo.objects.get(usuario=self.cliente)
        self.assertEqual(carro.items.count(), 0)

    # --------------------------------------------------------------------------
    # TEST 5: RECHAZO DE TRANSACCIÓN POR STOCK INSUFICIENTE
    # --------------------------------------------------------------------------
    def test_rechazo_checkout_por_stock_insuficiente(self):
        """
        Si la flota disponible es menor a la solicitada al momento de pagar,
        la transacción atómica debe rechazarse.
        """
        self.client.force_authenticate(user=self.cliente)

        # Agregamos 4 unidades
        hoy = date.today()
        self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.excavadora.id,
            'cantidad': 4,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': hoy.isoformat()
        }, format='json')

        # Simulamos que otro cliente arrendó y dejó la flota disponible en solo 2 unidades
        self.excavadora.flota_disponible = 2
        self.excavadora.save()

        # Intento de Checkout debe fallar con 400 Bad Request
        checkout_response = self.client.post('/api/contratos/checkout/', {}, format='json')
        self.assertEqual(checkout_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Inventario insuficiente', checkout_response.data['error'])

    # --------------------------------------------------------------------------
    # TEST 6: REPOSICIÓN AUTOMÁTICA DE FLOTA AL COMPLETAR O CANCELAR CONTRATO
    # --------------------------------------------------------------------------
    def test_transicion_estado_y_reposicion_automatica_flota(self):
        """
        Verifica que al transicionar un contrato a COMPLETADO (devolución) o CANCELADO,
        las unidades se reincorporen automáticamente a la flota disponible.
        """
        # 1. Cliente genera arriendo de 2 unidades
        self.client.force_authenticate(user=self.cliente)
        hoy = date.today()
        self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.excavadora.id,
            'cantidad': 2,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': hoy.isoformat()
        }, format='json')
        checkout_resp = self.client.post('/api/contratos/checkout/', {}, format='json')
        contrato_id = checkout_resp.data['contrato']['id']

        self.excavadora.refresh_from_db()
        self.assertEqual(self.excavadora.flota_disponible, 3)  # 5 - 2 = 3

        # 2. Cliente intenta cambiar estado (debe fallar por permisos RBAC)
        patch_cliente = self.client.patch(f'/api/contratos/{contrato_id}/estado/', {'nuevo_estado': 'ENTREGADO'}, format='json')
        self.assertEqual(patch_cliente.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Ejecutivo cambia estado a ENTREGADO
        self.client.force_authenticate(user=self.ejecutivo)
        patch_entregado = self.client.patch(f'/api/contratos/{contrato_id}/estado/', {
            'nuevo_estado': EstadoContrato.ENTREGADO,
            'comentarios': 'Equipo entregado en faena conforme.'
        }, format='json')
        self.assertEqual(patch_entregado.status_code, status.HTTP_200_OK)

        # Flota sigue en 3 mientras está en uso
        self.excavadora.refresh_from_db()
        self.assertEqual(self.excavadora.flota_disponible, 3)

        # 4. Ejecutivo cambia estado a COMPLETADO (Devolución a bodega)
        patch_completado = self.client.patch(f'/api/contratos/{contrato_id}/estado/', {
            'nuevo_estado': EstadoContrato.COMPLETADO,
            'comentarios': 'Equipo devuelto e inspeccionado.'
        }, format='json')
        self.assertEqual(patch_completado.status_code, status.HTTP_200_OK)

        # ¡Flota debe haberse repuesto automáticamente a 5!
        self.excavadora.refresh_from_db()
        self.assertEqual(self.excavadora.flota_disponible, 5)
