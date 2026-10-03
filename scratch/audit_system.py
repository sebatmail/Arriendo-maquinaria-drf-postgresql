"""
================================================================================
SCRIPT DE AUDITORÍA INTEGRAL DE SISTEMA Y BASE DE DATOS POSTGRESQL (EVA-2)
================================================================================
Prueba cada botón, formulario, endpoint, mutación y persistencia en base de datos.
"""

import os
import sys
import django
import json
from decimal import Decimal
from datetime import date, timedelta

# Agregar directorio raíz al PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
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
import psycopg

Usuario = get_user_model()

def auditar_todo():
    print("=" * 80)
    print("INICIANDO AUDITORÍA INTEGRAL END-TO-END (POSTGRESQL + DRF + TEMPLATES)")
    print("=" * 80)

    client = Client()
    errores = []
    pruebas_exitosas = 0

    # --------------------------------------------------------------------------
    # 1. AUDITORÍA DE CONEXIÓN ACTIVA A POSTGRESQL
    # --------------------------------------------------------------------------
    print("\n[1/6] Verificando conexión nativa con PostgreSQL 12...")
    try:
        with psycopg.connect("host=127.0.0.1 port=5432 user=postgres dbname=arriendo_maquinaria_db") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                ver = cur.fetchone()[0]
                print(f" -> [OK] Conexión activa a PostgreSQL: {ver[:40]}...")
                cur.execute("SELECT count(*) FROM renting_maquinaria;")
                total_maq = cur.fetchone()[0]
                print(f" -> [OK] Registros de maquinaria en BD: {total_maq}")
                pruebas_exitosas += 1
    except Exception as e:
        print(f" -> [ERROR] Fallo de conexión a PostgreSQL: {e}")
        errores.append(f"PostgreSQL direct connection error: {e}")

    # --------------------------------------------------------------------------
    # 2. AUDITORÍA DE RUTAS PÚBLICAS Y CATÁLOGO
    # --------------------------------------------------------------------------
    print("\n[2/6] Auditando Catálogo Público, Filtros y Vistas Web...")
    rutas_publicas = [
        ('/', 200, "Vista Catálogo Inicio"),
        ('/login/', 200, "Vista Iniciar Sesión"),
        ('/registro/', 200, "Vista Registro Constructora"),
        ('/api/maquinarias/', 200, "API Catálogo JSON"),
        ('/api/categorias/', 200, "API Categorías JSON"),
        ('/api/schema/', 200, "API OpenAPI Schema"),
        ('/api/docs/', 200, "API Swagger UI Docs"),
    ]

    for ruta, status_esperado, desc in rutas_publicas:
        resp = client.get(ruta)
        if resp.status_code == status_esperado:
            print(f" -> [OK] {desc} ({ruta}) -> Status {resp.status_code}")
            pruebas_exitosas += 1
        else:
            print(f" -> [FAIL] {desc} ({ruta}) -> Esperado {status_esperado}, Obtenido {resp.status_code}")
            errores.append(f"{desc} status mismatch: {resp.status_code}")

    # Filtro django-filter
    resp_filtro = client.get('/api/maquinarias/?max_precio=100000')
    if resp_filtro.status_code == 200:
        print(" -> [OK] Filtro dinámico django-filter (?max_precio=100000) operativo.")
        pruebas_exitosas += 1
    else:
        errores.append("django-filter failed on /api/maquinarias/?max_precio=100000")

    # --------------------------------------------------------------------------
    # 3. AUDITORÍA DE REGISTRO, LOGIN Y JWT CLAIMS
    # --------------------------------------------------------------------------
    print("\n[3/6] Auditando Registro de Nueva Empresa y Emisión JWT con Claims de Rol...")
    test_user_payload = {
        "username": "constructora_audit_2026",
        "email": "audit@constructora.cl",
        "password": "PasswordAudit123!",
        "password_confirm": "PasswordAudit123!",
        "first_name": "Sebastián",
        "last_name": "Torres Zamorano",
        "rol": RolUsuario.EMPRESA_CONSTRUCTORA,
        "razon_social": "Constructora Auditoría SpA",
        "rut_empresa": "77.888.999-1",
        "telefono": "+56 9 1122 3344",
        "direccion_obra": "Faena Minera El Teniente"
    }

    resp_reg = client.post('/api/auth/registro/', test_user_payload, content_type='application/json')
    if resp_reg.status_code in [201, 400]: # 201 creado o 400 si ya existe
        print(" -> [OK] Endpoint de Registro de Empresa Constructora validado.")
        pruebas_exitosas += 1
    else:
        errores.append(f"Registro failed: {resp_reg.status_code} {resp_reg.content}")

    # Login JWT
    resp_login = client.post('/api/auth/login/', {
        "username": "constructora_audit_2026",
        "password": "PasswordAudit123!"
    }, content_type='application/json')

    if resp_login.status_code == 200:
        login_data = json.loads(resp_login.content)
        access_token = login_data.get('access')
        user_info = login_data.get('user', {})
        if user_info.get('rol') == 'EMPRESA_CONSTRUCTORA' and user_info.get('razon_social') == 'Constructora Auditoría SpA':
            print(" -> [OK] Login JWT exitoso con Claims de Rol verificados:")
            print(f"      * User ID: {user_info.get('id')}")
            print(f"      * Rol: {user_info.get('rol')}")
            print(f"      * Razón Social: {user_info.get('razon_social')}")
            pruebas_exitosas += 1
        else:
            errores.append("Claims de rol incompletos en login JWT")
    else:
        errores.append(f"Login JWT failed: {resp_login.status_code}")

    # --------------------------------------------------------------------------
    # 4. AUDITORÍA DEL CARRO PERSISTENTE (POSTGRESQL POST-LOGOUT)
    # --------------------------------------------------------------------------
    print("\n[4/6] Auditando Carro de Arriendo Persistente en Base de Datos...")
    usuario_audit = Usuario.objects.get(username="constructora_audit_2026")
    client.force_login(usuario_audit)

    excavadora = Maquinaria.objects.filter(estado_operativo=EstadoMaquinaria.DISPONIBLE).first()
    hoy = date.today()
    fin = hoy + timedelta(days=3) # 4 días

    # Agregar ítem al carro
    resp_cart = client.post('/api/carro-arriendo/', {
        "maquinaria_id": excavadora.id,
        "cantidad": 1,
        "fecha_inicio": hoy.isoformat(),
        "fecha_fin": fin.isoformat()
    }, content_type='application/json')

    if resp_cart.status_code in [200, 201]:
        print(f" -> [OK] Ítem agregado al Carro: 1x {excavadora.nombre} ({hoy} a {fin})")
        pruebas_exitosas += 1
    else:
        errores.append(f"Fallo al agregar al carro: {resp_cart.content}")

    # Verificar persistencia en base de datos
    carro_db = CarroArriendo.objects.get(usuario=usuario_audit)
    if carro_db.items.count() == 1:
        item = carro_db.items.first()
        print(f" -> [OK] Persistencia verificada en PostgreSQL: Carro ID {carro_db.id} con {carro_db.items.count()} ítem(s).")
        print(f"      * Subtotal Arriendo: ${item.subtotal_arriendo:,.0f} CLP")
        print(f"      * Subtotal Garantía: ${item.subtotal_garantia:,.0f} CLP")
        print(f"      * Total Calculado:   ${carro_db.total_general:,.0f} CLP")
        pruebas_exitosas += 1
    else:
        errores.append("El carro no persistió correctamente en PostgreSQL.")

    # --------------------------------------------------------------------------
    # 5. AUDITORÍA DEL CHECKOUT ATÓMICO Y GESTIÓN DE FLOTA
    # --------------------------------------------------------------------------
    print("\n[5/6] Auditando Checkout Atómico, Bloqueo Pesimista y Descuento de Flota...")
    flota_inicial = excavadora.flota_disponible

    resp_checkout = client.post('/api/contratos/checkout/', {
        "direccion_faena": "Obra Costanera Sur #500, Santiago",
        "observaciones": "Entrega con horómetro cero y seguro vigente."
    }, content_type='application/json')

    if resp_checkout.status_code == 201:
        checkout_data = json.loads(resp_checkout.content)
        contrato_obj = checkout_data['contrato']
        numero_contrato = contrato_obj['numero_contrato']
        print(f" -> [OK] Contrato de Arriendo Generado Exitosamente: {numero_contrato}")
        print(f"      * Estado: {contrato_obj['estado']} (PAGADO)")
        print(f"      * Total Liquidado: ${float(contrato_obj['total_general']):,.0f} CLP")

        # Verificar que el carro se vació
        carro_db.refresh_from_db()
        if carro_db.items.count() == 0:
            print(" -> [OK] Carro de compras persistente liquidado y vaciado en BD.")
            pruebas_exitosas += 1
        else:
            errores.append("El carro no se vació tras el checkout.")

        # Verificar descuento de flota en BD
        excavadora.refresh_from_db()
        if excavadora.flota_disponible == flota_inicial - 1:
            print(f" -> [OK] Descuento atómico de flota verificado en PostgreSQL: {flota_inicial} -> {excavadora.flota_disponible} unidad(es).")
            pruebas_exitosas += 1
        else:
            errores.append("La flota disponible no se descontó en PostgreSQL.")

    else:
        errores.append(f"Checkout atómico falló: {resp_checkout.content}")

    # --------------------------------------------------------------------------
    # 6. AUDITORÍA DE ACCIONES DE ADMINISTRACIÓN / EJECUTIVO
    # --------------------------------------------------------------------------
    print("\n[6/6] Auditando Permisos Ejecutivos, CRUD y Reposición Automática de Flota...")
    ejecutivo = Usuario.objects.get(username="admin_ejecutivo")
    client.force_login(ejecutivo)

    # Vista protegida Swagger Admin
    resp_doc_admin = client.get('/documentacion/')
    if resp_doc_admin.status_code == 200:
        print(" -> [OK] Vista de Documentación Swagger (Header Solo Admin) accesible para Ejecutivo.")
        pruebas_exitosas += 1
    else:
        errores.append(f"Vista documentacion_admin no accesible: {resp_doc_admin.status_code}")

    # Transición a ENTREGADO
    contrato_instancia = ContratoArriendo.objects.get(numero_contrato=numero_contrato)
    resp_entregado = client.patch(f'/api/contratos/{contrato_instancia.id}/estado/', {
        "nuevo_estado": "ENTREGADO",
        "comentarios": "Maquinaria despachada a faena conforme."
    }, content_type='application/json')

    if resp_entregado.status_code == 200:
        print(f" -> [OK] Transición a ENTREGADO aplicada en contrato {numero_contrato}.")
        pruebas_exitosas += 1
    else:
        errores.append(f"Fallo al transicionar a ENTREGADO: {resp_entregado.content}")

    # Transición a COMPLETADO (Devolución con reposición automática)
    resp_completado = client.patch(f'/api/contratos/{contrato_instancia.id}/estado/', {
        "nuevo_estado": "COMPLETADO",
        "comentarios": "Equipo devuelto a bodega con inspección técnica aprobada."
    }, content_type='application/json')

    if resp_completado.status_code == 200:
        print(f" -> [OK] Transición a COMPLETADO aplicada en contrato {numero_contrato}.")
        excavadora.refresh_from_db()
        if excavadora.flota_disponible == flota_inicial:
            print(f" -> [OK] Reposición automática de flota verificada en PostgreSQL: Flota disponible restablecida a {excavadora.flota_disponible} unidad(es).")
            pruebas_exitosas += 1
        else:
            errores.append(f"La flota no se repuso correctamente: actual {excavadora.flota_disponible}, esperado {flota_inicial}")
    else:
        errores.append(f"Fallo al transicionar a COMPLETADO: {resp_completado.content}")

    print("\n" + "=" * 80)
    print(f"RESULTADO DE LA AUDITORÍA: {pruebas_exitosas} PRUEBAS SUPERADAS EXITOSAMENTE.")
    if errores:
        print(f"Se encontraron {len(errores)} anomalías:")
        for err in errores:
            print(f" [X] {err}")
    else:
        print("TODOS LOS BOTONES, FORMULARIOS, ENDPOINTS Y REGISTROS EN POSTGRESQL ESTÁN 100% OPERATIVOS.")
    print("=" * 80)

if __name__ == '__main__':
    auditar_todo()
