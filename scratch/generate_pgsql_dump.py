"""
Generador del archivo SQL nativo para PostgreSQL / phpPgAdmin en cPanel
Base de datos: altoplagas_Proyecto_Backend
"""

import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password

pass_admin_hash = make_password('admin1234')
pass_demo_hash = make_password('demo1234')

pg_sql_content = f"""-- =============================================================================
-- BASE DE DATOS: altoplagas_Proyecto_Backend (POSTGRESQL / phpPgAdmin)
-- PLATAFORMA: RENT-EQUIP PRO Enterprise (Momentum Space)
-- COMPATIBILIDAD: PostgreSQL 10+ / PostgreSQL 12+ / PostgreSQL 14+ / phpPgAdmin
-- =============================================================================

-- 1. TABLA: authentication_usuario
DROP TABLE IF EXISTS authentication_usuario CASCADE;
CREATE TABLE authentication_usuario (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rol VARCHAR(30) NOT NULL DEFAULT 'EMPRESA_CONSTRUCTORA',
    rut_empresa VARCHAR(20) NULL,
    razon_social VARCHAR(150) NULL,
    telefono VARCHAR(20) NULL,
    direccion_obra VARCHAR(255) NULL
);

-- 2. TABLA: renting_categoriaequipo
DROP TABLE IF EXISTS renting_categoriaequipo CASCADE;
CREATE TABLE renting_categoriaequipo (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL DEFAULT '',
    icono VARCHAR(50) NOT NULL DEFAULT 'fa-tools',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: renting_maquinaria
DROP TABLE IF EXISTS renting_maquinaria CASCADE;
CREATE TABLE renting_maquinaria (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo_sku VARCHAR(50) NOT NULL UNIQUE,
    marca VARCHAR(100) NOT NULL DEFAULT 'Caterpillar',
    modelo VARCHAR(100) NOT NULL DEFAULT 'Standard',
    descripcion TEXT NOT NULL,
    tarifa_diaria NUMERIC(12,2) NOT NULL,
    monto_garantia NUMERIC(12,2) NOT NULL,
    flota_total INTEGER NOT NULL DEFAULT 1,
    flota_disponible INTEGER NOT NULL DEFAULT 1,
    estado_operativo VARCHAR(20) NOT NULL DEFAULT 'DISPONIBLE',
    imagen_url VARCHAR(500) NOT NULL DEFAULT '',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    categoria_id BIGINT NOT NULL REFERENCES renting_categoriaequipo(id) ON DELETE RESTRICT
);

-- 4. TABLA: renting_carroarriendo
DROP TABLE IF EXISTS renting_carroarriendo CASCADE;
CREATE TABLE renting_carroarriendo (
    id BIGSERIAL PRIMARY KEY,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id BIGINT NOT NULL UNIQUE REFERENCES authentication_usuario(id) ON DELETE CASCADE
);

-- 5. TABLA: renting_itemcarroarriendo
DROP TABLE IF EXISTS renting_itemcarroarriendo CASCADE;
CREATE TABLE renting_itemcarroarriendo (
    id BIGSERIAL PRIMARY KEY,
    cantidad INTEGER NOT NULL DEFAULT 1,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    carro_id BIGINT NOT NULL REFERENCES renting_carroarriendo(id) ON DELETE CASCADE,
    maquinaria_id BIGINT NOT NULL REFERENCES renting_maquinaria(id) ON DELETE CASCADE,
    CONSTRAINT unique_maquinaria_por_carro UNIQUE (carro_id, maquinaria_id)
);

-- 6. TABLA: renting_contratoarriendo
DROP TABLE IF EXISTS renting_contratoarriendo CASCADE;
CREATE TABLE renting_contratoarriendo (
    id UUID PRIMARY KEY,
    numero_contrato VARCHAR(30) NOT NULL UNIQUE,
    estado VARCHAR(20) NOT NULL DEFAULT 'PAGADO',
    total_arriendo NUMERIC(14,2) NOT NULL,
    total_garantias NUMERIC(14,2) NOT NULL,
    total_general NUMERIC(14,2) NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pagado_en TIMESTAMPTZ NULL,
    entregado_en TIMESTAMPTZ NULL,
    completado_en TIMESTAMPTZ NULL,
    cancelado_en TIMESTAMPTZ NULL,
    direccion_faena VARCHAR(255) NOT NULL DEFAULT '',
    observaciones TEXT NOT NULL DEFAULT '',
    cliente_id BIGINT NOT NULL REFERENCES authentication_usuario(id) ON DELETE RESTRICT
);

-- 7. TABLA: renting_detallecontratoarriendo
DROP TABLE IF EXISTS renting_detallecontratoarriendo CASCADE;
CREATE TABLE renting_detallecontratoarriendo (
    id BIGSERIAL PRIMARY KEY,
    nombre_equipo_congelado VARCHAR(200) NOT NULL,
    codigo_sku_congelado VARCHAR(50) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_totales INTEGER NOT NULL,
    tarifa_diaria_congelada NUMERIC(12,2) NOT NULL,
    monto_garantia_congelado NUMERIC(12,2) NOT NULL,
    subtotal_arriendo NUMERIC(14,2) NOT NULL,
    subtotal_garantia NUMERIC(14,2) NOT NULL,
    total_linea NUMERIC(14,2) NOT NULL,
    contrato_id UUID NOT NULL REFERENCES renting_contratoarriendo(id) ON DELETE CASCADE,
    maquinaria_id BIGINT NOT NULL REFERENCES renting_maquinaria(id) ON DELETE RESTRICT
);

-- 8. TABLA: renting_historialtransicioncontrato
DROP TABLE IF EXISTS renting_historialtransicioncontrato CASCADE;
CREATE TABLE renting_historialtransicioncontrato (
    id BIGSERIAL PRIMARY KEY,
    estado_anterior VARCHAR(30) NOT NULL,
    estado_nuevo VARCHAR(30) NOT NULL,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comentarios TEXT NOT NULL DEFAULT '',
    cambiado_por_id BIGINT NULL REFERENCES authentication_usuario(id) ON DELETE SET NULL,
    contrato_id UUID NOT NULL REFERENCES renting_contratoarriendo(id) ON DELETE CASCADE
);

-- =============================================================================
-- INSERCIÓN DE DATOS INICIALES (POSTGRESQL)
-- =============================================================================

-- 1. Usuarios Demo
INSERT INTO authentication_usuario (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, rol, rut_empresa, razon_social, telefono, direccion_obra) VALUES
(1, '{pass_admin_hash}', TRUE, 'admin_ejecutivo', 'Administrador', 'Ejecutivo', 'ejecutivo@momentumspace.cl', TRUE, TRUE, CURRENT_TIMESTAMP, 'EJECUTIVO_ARRIENDOS', '76.999.888-K', 'Rent-Equip Pro SpA - Casa Matriz', '+56 2 2999 1100', 'Av. Apoquindo 4500, Las Condes'),
(2, '{pass_demo_hash}', FALSE, 'constructora_demo', 'Sebastián', 'Torres Zamorano', 'contacto@pacificospa.cl', FALSE, TRUE, CURRENT_TIMESTAMP, 'EMPRESA_CONSTRUCTORA', '76.452.120-3', 'Constructora Del Pacífico SpA', '+56 9 8451 9021', 'Autopista Nororiente Km 14, Santiago');

-- 2. Categorías Industriales
INSERT INTO renting_categoriaequipo (id, nombre, slug, descripcion, icono, creado_en) VALUES
(1, 'Maquinaria Pesada', 'maquinaria-pesada', 'Excavadoras de orugas, retroexcavadoras y cargadores frontales de alto tonelaje.', 'fa-tractor', CURRENT_TIMESTAMP),
(2, 'Generación Eléctrica', 'generacion-electrica', 'Grupos electrógenos diésel insonorizados y torres móviles de iluminación LED.', 'fa-bolt', CURRENT_TIMESTAMP),
(3, 'Andamios y Estructuras', 'andamios-y-estructuras', 'Sistemas de andamiaje multidireccional Layher certificados bajo norma europea.', 'fa-cubes', CURRENT_TIMESTAMP),
(4, 'Hormigón y Pavimento', 'hormigon-y-pavimento', 'Plantas de hormigón móviles autocargables, camiones mixer y alisadoras dobles.', 'fa-gem', CURRENT_TIMESTAMP);

-- 3. Catálogo de Maquinarias
INSERT INTO renting_maquinaria (id, nombre, codigo_sku, marca, modelo, descripcion, tarifa_diaria, monto_garantia, flota_total, flota_disponible, estado_operativo, imagen_url, creado_en, actualizado_en, categoria_id) VALUES
(1, 'Excavadora Hidráulica CAT 320 GC', 'MAQ-EXC-320', 'Caterpillar', '320 GC Tier 4', 'Excavadora de 20 toneladas con motor Cat C4.4 ACERT de 146 hp. Balde de 1.19 m3, ideal para zanjeo, carga masiva de camiones y movimientos de tierra exigentes.', 185000.00, 850000.00, 6, 4, 'DISPONIBLE', 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
(2, 'Retroexcavadora JCB 3CX Eco 4x4', 'MAQ-RET-3CX', 'JCB', '3CX Super 4WD', 'Retroexcavadora versátil con tracción en las 4 ruedas, brazo extensible de 5.46 m de profundidad y balde frontal de 1.0 m3. Incluye enganche rápido para martillo hidráulico.', 120000.00, 500000.00, 8, 6, 'DISPONIBLE', 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
(3, 'Generador Diésel Cummins 150 kVA Insonorizado', 'GEN-CUM-150', 'Cummins Power', 'C150D5', 'Grupo electrógeno trifásico de 150 kVA con cabina insonorizada ultra silenciosa (68 dBA @ 7m). Panel digital Deep Sea y estanque de combustible de 24 horas continuas.', 95000.00, 400000.00, 10, 7, 'DISPONIBLE', 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2),
(4, 'Torre de Iluminación LED Atlas Copco HiLight V4+', 'ILU-ATL-V4', 'Atlas Copco', 'HiLight V4+ LED', 'Torre de iluminación móvil con 4 proyectores LED de 350W capaces de iluminar 5.000 m2. Mástil hidráulico extensible hasta 8 metros de altura.', 45000.00, 200000.00, 12, 9, 'DISPONIBLE', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2),
(5, 'Sistema de Andamio Multidireccional Layher Allround 12m', 'AND-LAY-12M', 'Layher', 'Allround HD', 'Módulo de andamio multidireccional de acero galvanizado con 12 metros de altura de trabajo. Certificado bajo norma europea EN 12810/12811 con plataformas antideslizantes.', 38000.00, 180000.00, 20, 15, 'DISPONIBLE', 'https://images.unsplash.com/photo-1541971875076-8f970d573be6?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3),
(6, 'Hormigonera Autocargable Carmix 2.5 TT 4x4', 'HOR-CAR-25T', 'Carmix', '2.5 TT All-Terrain', 'Planta de hormigón móvil 4x4 con pala autocargable y capacidad de tambor de 3.450 litros (rendimiento 2.5 m3 por ciclo). Sistema de pesaje electrónico computarizado.', 165000.00, 750000.00, 5, 3, 'DISPONIBLE', 'https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 4),
(7, 'Alisadora de Pavimento Doble Wacker Neuson CRT48', 'ALI-WAC-CRT', 'Wacker Neuson', 'CRT 48-35VX', 'Helicóptero alisador de hormigón de operador sentado con doble rotor de 48 pulgadas y motor Briggs & Stratton Vanguard de 35 hp. Terminación de piso superplana.', 75000.00, 320000.00, 7, 5, 'DISPONIBLE', 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 4);

-- 4. Carros de Arriendo Iniciales
INSERT INTO renting_carroarriendo (id, creado_en, actualizado_en, usuario_id) VALUES
(1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
(2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2);

-- 5. Contrato Histórico Demo
INSERT INTO renting_contratoarriendo (id, numero_contrato, estado, total_arriendo, total_garantias, total_general, creado_en, pagado_en, direccion_faena, observaciones, cliente_id) VALUES
('c7a8e912-3456-7890-abcd-ef1234567890', 'CTR-2026-A1B2C3D4', 'PAGADO', 1400000.00, 1250000.00, 2650000.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Túnel Vespucio Oriente Km 12, Santiago', 'Contrato inicial con póliza de seguro y operadores certificados.', 2);

-- 6. Detalles del Contrato (Snapshots Inmutables 3FN)
INSERT INTO renting_detallecontratoarriendo (id, nombre_equipo_congelado, codigo_sku_congelado, cantidad, fecha_inicio, fecha_fin, dias_totales, tarifa_diaria_congelada, monto_garantia_congelado, subtotal_arriendo, subtotal_garantia, total_linea, contrato_id, maquinaria_id) VALUES
(1, 'Excavadora Hidráulica CAT 320 GC', 'MAQ-EXC-320', 1, CURRENT_DATE, CURRENT_DATE + INTERVAL '4 days', 5, 185000.00, 850000.00, 925000.00, 850000.00, 1775000.00, 'c7a8e912-3456-7890-abcd-ef1234567890', 1),
(2, 'Generador Diésel Cummins 150 kVA Insonorizado', 'GEN-CUM-150', 1, CURRENT_DATE, CURRENT_DATE + INTERVAL '4 days', 5, 95000.00, 400000.00, 475000.00, 400000.00, 875000.00, 'c7a8e912-3456-7890-abcd-ef1234567890', 3);

-- 7. Historial de Auditoría
INSERT INTO renting_historialtransicioncontrato (id, estado_anterior, estado_nuevo, fecha_registro, comentarios, cambiado_por_id, contrato_id) VALUES
(1, 'INICIAL (CARRO)', 'PAGADO', CURRENT_TIMESTAMP, 'Checkout exitoso con descuento atómico de flota.', 2, 'c7a8e912-3456-7890-abcd-ef1234567890');
"""

output_path_pg = r'c:\Users\Lenovo Legion T5\Desktop\EVA 2 BACKEND LOGISTICA DJANGO\altoplagas_Proyecto_Backend_POSTGRESQL.sql'
desktop_path_pg = r'C:\Users\Lenovo Legion T5\Desktop\altoplagas_Proyecto_Backend_POSTGRESQL.sql'

with open(output_path_pg, 'w', encoding='utf-8') as f:
    f.write(pg_sql_content)

with open(desktop_path_pg, 'w', encoding='utf-8') as f:
    f.write(pg_sql_content)

print(f"SQL PostgreSQL generado exitosamente en:\n - {output_path_pg}\n - {desktop_path_pg}")
