"""
================================================================================
COMANDO DE POBLAMIENTO INICIAL DE DATOS (SEED DATA)
================================================================================
Genera usuarios por rol, categorías industriales, maquinarias con tarifas y garantías,
y contratos de prueba para evaluación inmediata del sistema.
"""

from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from authentication.models import RolUsuario
from renting.models import (
    CategoriaEquipo,
    Maquinaria,
    EstadoMaquinaria,
    CarroArriendo,
    ItemCarroArriendo,
    ContratoArriendo,
    DetalleContratoArriendo,
    HistorialTransicionContrato,
    EstadoContrato
)

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Puebla la base de datos con categorías, equipos, usuarios de prueba y contratos históricos.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Inicializando sembrado de datos en PostgreSQL...'))

        # 1. Crear Usuarios de Prueba (Ejecutivo y Constructoras)
        ejecutivo, _ = Usuario.objects.get_or_create(
            username='admin_ejecutivo',
            defaults={
                'email': 'ejecutivo@rent-equip.pro',
                'first_name': 'Roberto',
                'last_name': 'Vargas',
                'rol': RolUsuario.EJECUTIVO_ARRIENDOS,
                'razon_social': 'Rent-Equip Pro SpA - Casa Matriz',
                'rut_empresa': '76.999.888-K',
                'telefono': '+56 2 2999 1100',
                'is_staff': True,
                'is_superuser': True
            }
        )
        ejecutivo.set_password('admin1234')
        ejecutivo.save()

        cliente1, _ = Usuario.objects.get_or_create(
            username='constructora_demo',
            defaults={
                'email': 'contacto@pacificospa.cl',
                'first_name': 'Sebastián',
                'last_name': 'Tapia',
                'rol': RolUsuario.EMPRESA_CONSTRUCTORA,
                'razon_social': 'Constructora Del Pacífico SpA',
                'rut_empresa': '76.452.120-3',
                'telefono': '+56 9 8451 9021',
                'direccion_obra': 'Proyecto Autopista Nororiente Km 14, Santiago',
                'is_staff': False
            }
        )
        cliente1.set_password('demo1234')
        cliente1.save()

        cliente2, _ = Usuario.objects.get_or_create(
            username='constructora_andes',
            defaults={
                'email': 'obras@consorcioandes.cl',
                'first_name': 'Matías',
                'last_name': 'González',
                'rol': RolUsuario.EMPRESA_CONSTRUCTORA,
                'razon_social': 'Consorcio Minero Andino S.A.',
                'rut_empresa': '96.882.340-1',
                'telefono': '+56 9 7210 4455',
                'direccion_obra': 'Faena Minera Pelambres, Salamanca',
                'is_staff': False
            }
        )
        cliente2.set_password('demo1234')
        cliente2.save()

        # 2. Crear Categorías Industriales
        cat_pesada, _ = CategoriaEquipo.objects.get_or_create(
            slug='maquinaria-pesada',
            defaults={'nombre': 'Maquinaria Pesada', 'descripcion': 'Excavadoras, cargadores frontales y retroexcavadoras', 'icono': 'fa-tractor'}
        )
        cat_generacion, _ = CategoriaEquipo.objects.get_or_create(
            slug='generacion-electrica',
            defaults={'nombre': 'Generación Eléctrica', 'descripcion': 'Grupos electrógenos, motobombas y torres de luz', 'icono': 'fa-bolt'}
        )
        cat_andamios, _ = CategoriaEquipo.objects.get_or_create(
            slug='andamios-y-estructuras',
            defaults={'nombre': 'Andamios y Estructuras', 'descripcion': 'Sistemas Layher certificados y torres de acceso', 'icono': 'fa-cubes'}
        )
        cat_hormigon, _ = CategoriaEquipo.objects.get_or_create(
            slug='hormigon-y-pavimento',
            defaults={'nombre': 'Hormigón y Pavimento', 'descripcion': 'Hormigoneras autocargables, camiones mixer y alisadoras', 'icono': 'fa-gem'}
        )

        # 3. Crear Catálogo de Maquinarias (Mencionadas en el PDF)
        maquinarias_data = [
            {
                'categoria': cat_pesada,
                'nombre': 'Excavadora Hidráulica CAT 320 GC',
                'codigo_sku': 'MAQ-EXC-320',
                'marca': 'Caterpillar',
                'modelo': '320 GC Tier 4',
                'descripcion': 'Excavadora de 20 toneladas con motor Cat C4.4 ACERT de 146 hp. Balde de 1.19 m3, ideal para zanjeo, carga masiva de camiones y movimientos de tierra exigentes.',
                'tarifa_diaria': Decimal('185000.00'),
                'monto_garantia': Decimal('850000.00'),
                'flota_total': 6,
                'flota_disponible': 4,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_pesada,
                'nombre': 'Retroexcavadora JCB 3CX Eco 4x4',
                'codigo_sku': 'MAQ-RET-3CX',
                'marca': 'JCB',
                'modelo': '3CX Super 4WD',
                'descripcion': 'Retroexcavadora versátil con tracción en las 4 ruedas, brazo extensible de 5.46 m de profundidad y balde frontal de 1.0 m3. Incluye enganche rápido para martillo hidráulico.',
                'tarifa_diaria': Decimal('120000.00'),
                'monto_garantia': Decimal('500000.00'),
                'flota_total': 8,
                'flota_disponible': 6,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_generacion,
                'nombre': 'Generador Diésel Cummins 150 kVA Insonorizado',
                'codigo_sku': 'GEN-CUM-150',
                'marca': 'Cummins Power',
                'modelo': 'C150D5',
                'descripcion': 'Grupo electrógeno trifásico de 150 kVA con cabina insonorizada ultra silenciosa (68 dBA @ 7m). Panel digital Deep Sea y estanque de combustible de 24 horas continuas.',
                'tarifa_diaria': Decimal('95000.00'),
                'monto_garantia': Decimal('400000.00'),
                'flota_total': 10,
                'flota_disponible': 7,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_generacion,
                'nombre': 'Torre de Iluminación LED Atlas Copco HiLight V4+',
                'codigo_sku': 'ILU-ATL-V4',
                'marca': 'Atlas Copco',
                'modelo': 'HiLight V4+ LED',
                'descripcion': 'Torre de iluminación móvil con 4 proyectores LED de 350W capaces de iluminar 5.000 m2. Mástil hidráulico extensible hasta 8 metros de altura.',
                'tarifa_diaria': Decimal('45000.00'),
                'monto_garantia': Decimal('200000.00'),
                'flota_total': 12,
                'flota_disponible': 9,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_andamios,
                'nombre': 'Sistema de Andamio Multidireccional Layher Allround 12m',
                'codigo_sku': 'AND-LAY-12M',
                'marca': 'Layher',
                'modelo': 'Allround HD',
                'descripcion': 'Módulo de andamio multidireccional de acero galvanizado con 12 metros de altura de trabajo. Certificado bajo norma europea EN 12810/12811 con plataformas antideslizantes.',
                'tarifa_diaria': Decimal('38000.00'),
                'monto_garantia': Decimal('180000.00'),
                'flota_total': 20,
                'flota_disponible': 15,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1541971875076-8f970d573be6?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_hormigon,
                'nombre': 'Hormigonera Autocargable Carmix 2.5 TT 4x4',
                'codigo_sku': 'HOR-CAR-25T',
                'marca': 'Carmix',
                'modelo': '2.5 TT All-Terrain',
                'descripcion': 'Planta de hormigón móvil 4x4 con pala autocargable y capacidad de tambor de 3.450 litros (rendimiento 2.5 m3 por ciclo). Sistema de pesaje electrónico computarizado.',
                'tarifa_diaria': Decimal('165000.00'),
                'monto_garantia': Decimal('750000.00'),
                'flota_total': 5,
                'flota_disponible': 3,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=800&q=80'
            },
            {
                'categoria': cat_hormigon,
                'nombre': 'Alisadora de Pavimento Doble Wacker Neuson CRT48',
                'codigo_sku': 'ALI-WAC-CRT',
                'marca': 'Wacker Neuson',
                'modelo': 'CRT 48-35VX',
                'descripcion': 'Helicóptero alisador de hormigón de operador sentado con doble rotor de 48 pulgadas y motor Briggs & Stratton Vanguard de 35 hp. Terminación de piso superplana.',
                'tarifa_diaria': Decimal('75000.00'),
                'monto_garantia': Decimal('320000.00'),
                'flota_total': 7,
                'flota_disponible': 5,
                'estado_operativo': EstadoMaquinaria.DISPONIBLE,
                'imagen_url': 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80'
            }
        ]

        for m_data in maquinarias_data:
            Maquinaria.objects.update_or_create(
                codigo_sku=m_data['codigo_sku'],
                defaults=m_data
            )

        # 4. Crear Contrato Histórico de Ejemplo para Demostración
        excavadora = Maquinaria.objects.get(codigo_sku='MAQ-EXC-320')
        generador = Maquinaria.objects.get(codigo_sku='GEN-CUM-150')

        if not ContratoArriendo.objects.filter(cliente=cliente1).exists():
            contrato_demo = ContratoArriendo.objects.create(
                cliente=cliente1,
                estado=EstadoContrato.PAGADO,
                total_arriendo=Decimal('185000.00') * 5 + Decimal('95000.00') * 5,
                total_garantias=Decimal('850000.00') + Decimal('400000.00'),
                total_general=Decimal('2650000.00'),
                pagado_en=timezone.now() - timedelta(days=2),
                direccion_faena='Obra Túnel Vespucio Oriente, Santiago',
                observaciones='Contrato inicial con póliza de seguro y operadores certificados.'
            )

            DetalleContratoArriendo.objects.create(
                contrato=contrato_demo,
                maquinaria=excavadora,
                nombre_equipo_congelado=excavadora.nombre,
                codigo_sku_congelado=excavadora.codigo_sku,
                cantidad=1,
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=4),
                dias_totales=5,
                tarifa_diaria_congelada=excavadora.tarifa_diaria,
                monto_garantia_congelado=excavadora.monto_garantia,
                subtotal_arriendo=Decimal('925000.00'),
                subtotal_garantia=Decimal('850000.00'),
                total_linea=Decimal('1775000.00')
            )

            DetalleContratoArriendo.objects.create(
                contrato=contrato_demo,
                maquinaria=generador,
                nombre_equipo_congelado=generador.nombre,
                codigo_sku_congelado=generador.codigo_sku,
                cantidad=1,
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=4),
                dias_totales=5,
                tarifa_diaria_congelada=generador.tarifa_diaria,
                monto_garantia_congelado=generador.monto_garantia,
                subtotal_arriendo=Decimal('475000.00'),
                subtotal_garantia=Decimal('400000.00'),
                total_linea=Decimal('875000.00')
            )

            HistorialTransicionContrato.objects.create(
                contrato=contrato_demo,
                estado_anterior='INICIAL (CARRO)',
                estado_nuevo=EstadoContrato.PAGADO,
                cambiado_por=cliente1,
                comentarios='Contrato generado mediante checkout transaccional atómico.'
            )

        self.stdout.write(self.style.SUCCESS('¡Sembrado de datos completado exitosamente!'))
        self.stdout.write(self.style.SUCCESS('Cuentas de prueba listas:'))
        self.stdout.write(self.style.SUCCESS('1. Ejecutivo (Admin): admin_ejecutivo / admin1234'))
        self.stdout.write(self.style.SUCCESS('2. Constructora (Cliente): constructora_demo / demo1234'))
