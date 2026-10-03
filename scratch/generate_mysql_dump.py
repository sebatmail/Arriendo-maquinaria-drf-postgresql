import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password

# Hash de contraseñas de producción
pass_admin_hash = make_password('admin1234')
pass_demo_hash = make_password('demo1234')

sql_content = f"""-- =============================================================================
-- BASE DE DATOS: altoplagas_Proyecto_Backend
-- PLATAFORMA: RENT-EQUIP PRO Enterprise (Momentum Space)
-- COMPATIBILIDAD: MySQL 5.7+ / MySQL 8.0+ / MariaDB 10.3+ / phpMyAdmin
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- -----------------------------------------------------------------------------
-- 1. TABLA: authentication_usuario (Modelo de Usuario Extendido con RBAC)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `authentication_usuario`;
CREATE TABLE `authentication_usuario` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `username` varchar(150) NOT NULL UNIQUE,
  `first_name` varchar(150) NOT NULL DEFAULT '',
  `last_name` varchar(150) NOT NULL DEFAULT '',
  `email` varchar(254) NOT NULL DEFAULT '',
  `is_staff` tinyint(1) NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `date_joined` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `rol` varchar(30) NOT NULL DEFAULT 'EMPRESA_CONSTRUCTORA',
  `rut_empresa` varchar(20) DEFAULT NULL,
  `razon_social` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion_obra` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. TABLA: renting_categoriaequipo (Categorías Industriales en 3FN)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_categoriaequipo`;
CREATE TABLE `renting_categoriaequipo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL UNIQUE,
  `slug` varchar(120) NOT NULL UNIQUE,
  `descripcion` longtext NOT NULL,
  `icono` varchar(50) NOT NULL DEFAULT 'fa-tools',
  `creado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. TABLA: renting_maquinaria (Catálogo de Flota e Inventario)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_maquinaria`;
CREATE TABLE `renting_maquinaria` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `codigo_sku` varchar(50) NOT NULL UNIQUE,
  `marca` varchar(100) NOT NULL DEFAULT 'Caterpillar',
  `modelo` varchar(100) NOT NULL DEFAULT 'Standard',
  `descripcion` longtext NOT NULL,
  `tarifa_diaria` decimal(12,2) NOT NULL,
  `monto_garantia` decimal(12,2) NOT NULL,
  `flota_total` int(10) unsigned NOT NULL DEFAULT 1,
  `flota_disponible` int(10) unsigned NOT NULL DEFAULT 1,
  `estado_operativo` varchar(20) NOT NULL DEFAULT 'DISPONIBLE',
  `imagen_url` varchar(500) NOT NULL DEFAULT '',
  `creado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `actualizado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `categoria_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `renting_maquinaria_categoria_id_fk` (`categoria_id`),
  CONSTRAINT `renting_maquinaria_categoria_id_fk` FOREIGN KEY (`categoria_id`) REFERENCES `renting_categoriaequipo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. TABLA: renting_carroarriendo (Carro Persistente 1:1 con Usuario)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_carroarriendo`;
CREATE TABLE `renting_carroarriendo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `creado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `actualizado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `usuario_id` bigint(20) NOT NULL UNIQUE,
  PRIMARY KEY (`id`),
  CONSTRAINT `renting_carroarriendo_usuario_id_fk` FOREIGN KEY (`usuario_id`) REFERENCES `authentication_usuario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. TABLA: renting_itemcarroarriendo (Líneas de Carro con Fechas)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_itemcarroarriendo`;
CREATE TABLE `renting_itemcarroarriendo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cantidad` int(10) unsigned NOT NULL DEFAULT 1,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `creado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `carro_id` bigint(20) NOT NULL,
  `maquinaria_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_maquinaria_por_carro` (`carro_id`,`maquinaria_id`),
  KEY `renting_itemcarroarriendo_maquinaria_id_fk` (`maquinaria_id`),
  CONSTRAINT `renting_itemcarroarriendo_carro_id_fk` FOREIGN KEY (`carro_id`) REFERENCES `renting_carroarriendo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `renting_itemcarroarriendo_maquinaria_id_fk` FOREIGN KEY (`maquinaria_id`) REFERENCES `renting_maquinaria` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. TABLA: renting_contratoarriendo (Contrato Histórico Inmutable)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_contratoarriendo`;
CREATE TABLE `renting_contratoarriendo` (
  `id` char(32) NOT NULL,
  `numero_contrato` varchar(30) NOT NULL UNIQUE,
  `estado` varchar(20) NOT NULL DEFAULT 'PAGADO',
  `total_arriendo` decimal(14,2) NOT NULL,
  `total_garantias` decimal(14,2) NOT NULL,
  `total_general` decimal(14,2) NOT NULL,
  `creado_en` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `pagado_en` datetime(6) DEFAULT NULL,
  `entregado_en` datetime(6) DEFAULT NULL,
  `completado_en` datetime(6) DEFAULT NULL,
  `cancelado_en` datetime(6) DEFAULT NULL,
  `direccion_faena` varchar(255) NOT NULL DEFAULT '',
  `observaciones` longtext NOT NULL,
  `cliente_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `renting_contratoarriendo_cliente_id_fk` (`cliente_id`),
  CONSTRAINT `renting_contratoarriendo_cliente_id_fk` FOREIGN KEY (`cliente_id`) REFERENCES `authentication_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 7. TABLA: renting_detallecontratoarriendo (Snapshot Histórico en 3FN)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_detallecontratoarriendo`;
CREATE TABLE `renting_detallecontratoarriendo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre_equipo_congelado` varchar(200) NOT NULL,
  `codigo_sku_congelado` varchar(50) NOT NULL,
  `cantidad` int(10) unsigned NOT NULL DEFAULT 1,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `dias_totales` int(10) unsigned NOT NULL,
  `tarifa_diaria_congelada` decimal(12,2) NOT NULL,
  `monto_garantia_congelado` decimal(12,2) NOT NULL,
  `subtotal_arriendo` decimal(14,2) NOT NULL,
  `subtotal_garantia` decimal(14,2) NOT NULL,
  `total_linea` decimal(14,2) NOT NULL,
  `contrato_id` char(32) NOT NULL,
  `maquinaria_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `renting_detallecontratoarriendo_contrato_id_fk` (`contrato_id`),
  KEY `renting_detallecontratoarriendo_maquinaria_id_fk` (`maquinaria_id`),
  CONSTRAINT `renting_detallecontratoarriendo_contrato_id_fk` FOREIGN KEY (`contrato_id`) REFERENCES `renting_contratoarriendo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `renting_detallecontratoarriendo_maquinaria_id_fk` FOREIGN KEY (`maquinaria_id`) REFERENCES `renting_maquinaria` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 8. TABLA: renting_historialtransicioncontrato (Auditoría de Estados)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `renting_historialtransicioncontrato`;
CREATE TABLE `renting_historialtransicioncontrato` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `estado_anterior` varchar(30) NOT NULL,
  `estado_nuevo` varchar(30) NOT NULL,
  `fecha_registro` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `comentarios` longtext NOT NULL,
  `cambiado_por_id` bigint(20) DEFAULT NULL,
  `contrato_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `renting_historialtransicioncontrato_cambiado_por_id_fk` (`cambiado_por_id`),
  KEY `renting_historialtransicioncontrato_contrato_id_fk` (`contrato_id`),
  CONSTRAINT `renting_historialtransicioncontrato_cambiado_por_id_fk` FOREIGN KEY (`cambiado_por_id`) REFERENCES `authentication_usuario` (`id`) ON DELETE SET NULL,
  CONSTRAINT `renting_historialtransicioncontrato_contrato_id_fk` FOREIGN KEY (`contrato_id`) REFERENCES `renting_contratoarriendo` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- INSERCIÓN DE DATOS INICIALES (SEMILLA DE PRODUCCIÓN)
-- =============================================================================

-- 1. Usuarios Demo de Acceso
INSERT INTO `authentication_usuario` (`id`, `password`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `rol`, `rut_empresa`, `razon_social`, `telefono`, `direccion_obra`) VALUES
(1, '{pass_admin_hash}', 1, 'admin_ejecutivo', 'Administrador', 'Ejecutivo', 'ejecutivo@momentumspace.cl', 1, 1, NOW(), 'EJECUTIVO_ARRIENDOS', '76.999.888-K', 'Rent-Equip Pro SpA - Casa Matriz', '+56 2 2999 1100', 'Av. Apoquindo 4500, Las Condes'),
(2, '{pass_demo_hash}', 0, 'constructora_demo', 'Sebastián', 'Torres Zamorano', 'contacto@pacificospa.cl', 0, 1, NOW(), 'EMPRESA_CONSTRUCTORA', '76.452.120-3', 'Constructora Del Pacífico SpA', '+56 9 8451 9021', 'Autopista Nororiente Km 14, Santiago');

-- 2. Categorías Industriales
INSERT INTO `renting_categoriaequipo` (`id`, `nombre`, `slug`, `descripcion`, `icono`, `creado_en`) VALUES
(1, 'Maquinaria Pesada', 'maquinaria-pesada', 'Excavadoras de orugas, retroexcavadoras y cargadores frontales de alto tonelaje.', 'fa-tractor', NOW()),
(2, 'Generación Eléctrica', 'generacion-electrica', 'Grupos electrógenos diésel insonorizados y torres móviles de iluminación LED.', 'fa-bolt', NOW()),
(3, 'Andamios y Estructuras', 'andamios-y-estructuras', 'Sistemas de andamiaje multidireccional Layher certificados bajo norma europea.', 'fa-cubes', NOW()),
(4, 'Hormigón y Pavimento', 'hormigon-y-pavimento', 'Plantas de hormigón móviles autocargables, camiones mixer y alisadoras dobles.', 'fa-gem', NOW());

-- 3. Catálogo de Maquinarias Industriales
INSERT INTO `renting_maquinaria` (`id`, `nombre`, `codigo_sku`, `marca`, `modelo`, `descripcion`, `tarifa_diaria`, `monto_garantia`, `flota_total`, `flota_disponible`, `estado_operativo`, `imagen_url`, `creado_en`, `actualizado_en`, `categoria_id`) VALUES
(1, 'Excavadora Hidráulica CAT 320 GC', 'MAQ-EXC-320', 'Caterpillar', '320 GC Tier 4', 'Excavadora de 20 toneladas con motor Cat C4.4 ACERT de 146 hp. Balde de 1.19 m3, ideal para zanjeo, carga masiva de camiones y movimientos de tierra exigentes.', 185000.00, 850000.00, 6, 4, 'DISPONIBLE', 'https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 1),
(2, 'Retroexcavadora JCB 3CX Eco 4x4', 'MAQ-RET-3CX', 'JCB', '3CX Super 4WD', 'Retroexcavadora versátil con tracción en las 4 ruedas, brazo extensible de 5.46 m de profundidad y balde frontal de 1.0 m3. Incluye enganche rápido para martillo hidráulico.', 120000.00, 500000.00, 8, 6, 'DISPONIBLE', 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 1),
(3, 'Generador Diésel Cummins 150 kVA Insonorizado', 'GEN-CUM-150', 'Cummins Power', 'C150D5', 'Grupo electrógeno trifásico de 150 kVA con cabina insonorizada ultra silenciosa (68 dBA @ 7m). Panel digital Deep Sea y estanque de combustible de 24 horas continuas.', 95000.00, 400000.00, 10, 7, 'DISPONIBLE', 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 2),
(4, 'Torre de Iluminación LED Atlas Copco HiLight V4+', 'ILU-ATL-V4', 'Atlas Copco', 'HiLight V4+ LED', 'Torre de iluminación móvil con 4 proyectores LED de 350W capaces de iluminar 5.000 m2. Mástil hidráulico extensible hasta 8 metros de altura.', 45000.00, 200000.00, 12, 9, 'DISPONIBLE', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 2),
(5, 'Sistema de Andamio Multidireccional Layher Allround 12m', 'AND-LAY-12M', 'Layher', 'Allround HD', 'Módulo de andamio multidireccional de acero galvanizado con 12 metros de altura de trabajo. Certificado bajo norma europea EN 12810/12811 con plataformas antideslizantes.', 38000.00, 180000.00, 20, 15, 'DISPONIBLE', 'https://images.unsplash.com/photo-1541971875076-8f970d573be6?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 3),
(6, 'Hormigonera Autocargable Carmix 2.5 TT 4x4', 'HOR-CAR-25T', 'Carmix', '2.5 TT All-Terrain', 'Planta de hormigón móvil 4x4 con pala autocargable y capacidad de tambor de 3.450 litros (rendimiento 2.5 m3 por ciclo). Sistema de pesaje electrónico computarizado.', 165000.00, 750000.00, 5, 3, 'DISPONIBLE', 'https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 4),
(7, 'Alisadora de Pavimento Doble Wacker Neuson CRT48', 'ALI-WAC-CRT', 'Wacker Neuson', 'CRT 48-35VX', 'Helicóptero alisador de hormigón de operador sentado con doble rotor de 48 pulgadas y motor Briggs & Stratton Vanguard de 35 hp. Terminación de piso superplana.', 75000.00, 320000.00, 7, 5, 'DISPONIBLE', 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80', NOW(), NOW(), 4);

-- 4. Carros de Arriendo Iniciales
INSERT INTO `renting_carroarriendo` (`id`, `creado_en`, `actualizado_en`, `usuario_id`) VALUES
(1, NOW(), NOW(), 1),
(2, NOW(), NOW(), 2);

-- 5. Contrato Histórico Demo
INSERT INTO `renting_contratoarriendo` (`id`, `numero_contrato`, `estado`, `total_arriendo`, `total_garantias`, `total_general`, `creado_en`, `pagado_en`, `direccion_faena`, `observaciones`, `cliente_id`) VALUES
('c7a8e91234567890abcdef1234567890', 'CTR-2026-A1B2C3D4', 'PAGADO', 1400000.00, 1250000.00, 2650000.00, NOW(), NOW(), 'Túnel Vespucio Oriente Km 12, Santiago', 'Contrato inicial con póliza de seguro y operadores certificados.', 2);

-- 6. Detalles del Contrato (Snapshots Inmutables 3FN)
INSERT INTO `renting_detallecontratoarriendo` (`id`, `nombre_equipo_congelado`, `codigo_sku_congelado`, `cantidad`, `fecha_inicio`, `fecha_fin`, `dias_totales`, `tarifa_diaria_congelada`, `monto_garantia_congelado`, `subtotal_arriendo`, `subtotal_garantia`, `total_linea`, `contrato_id`, `maquinaria_id`) VALUES
(1, 'Excavadora Hidráulica CAT 320 GC', 'MAQ-EXC-320', 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 5, 185000.00, 850000.00, 925000.00, 850000.00, 1775000.00, 'c7a8e91234567890abcdef1234567890', 1),
(2, 'Generador Diésel Cummins 150 kVA Insonorizado', 'GEN-CUM-150', 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 5, 95000.00, 400000.00, 475000.00, 400000.00, 875000.00, 'c7a8e91234567890abcdef1234567890', 3);

-- 7. Historial de Auditoría
INSERT INTO `renting_historialtransicioncontrato` (`id`, `estado_anterior`, `estado_nuevo`, `fecha_registro`, `comentarios`, `cambiado_por_id`, `contrato_id`) VALUES
(1, 'INICIAL (CARRO)', 'PAGADO', NOW(), 'Checkout exitoso con descuento atómico de flota.', 2, 'c7a8e91234567890abcdef1234567890');

SET FOREIGN_KEY_CHECKS = 1;
-- =============================================================================
-- FIN DEL VOLCADO SQL: altoplagas_Proyecto_Backend
-- =============================================================================
"""

output_path = r'c:\Users\Lenovo Legion T5\Desktop\EVA 2 BACKEND LOGISTICA DJANGO\altoplagas_Proyecto_Backend.sql'
desktop_path = r'C:\Users\Lenovo Legion T5\Desktop\altoplagas_Proyecto_Backend.sql'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(sql_content)

with open(desktop_path, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"SQL generado exitosamente en:\n - {output_path}\n - {desktop_path}")
