<div align="center">

# 🚜 RENT-EQUIP PRO | Enterprise Industrial SaaS
### **Plataforma de Arriendo de Maquinaria Pesada en 3FN con Django REST Framework & PostgreSQL**
**Evaluación Backend EVA-2 (25% Ponderación Total • Puntaje: 100/100 • Nota 7.0)**

---

[![Live Demo](https://img.shields.io/badge/Live%20SaaS%20Web-PRODUCCI%C3%93N%20ACTIVA%20(ONLINE)-success?style=for-the-badge&logo=googlechrome&logoColor=white)](https://proyecto-backend.momentumspace.cl/)
[![Django Version](https://img.shields.io/badge/Django-3.2%20%7C%205.0%2B-092e20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST-3.15%2B-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B%20Native-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT Auth](https://img.shields.io/badge/Auth-SimpleJWT%20RBAC-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![OpenAPI](https://img.shields.io/badge/API%20Docs-OpenAPI%203.0%20%2F%20Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://proyecto-backend.momentumspace.cl/api/docs/)
[![Architecture](https://img.shields.io/badge/Architecture-3FN%20Normalized-f59e0b?style=for-the-badge&logo=speedtest&logoColor=black)](#)
[![Tests Status](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#)

<p align="center">
  <b>🚀 Plataforma SaaS Operando en Producción Web (En Vivo):</b><br>
  <a href="https://proyecto-backend.momentumspace.cl/"><b>👉 https://proyecto-backend.momentumspace.cl/ 👈</b></a><br><br>
  <b>🌐 Visita mi sitio web oficial:</b><br>
  <a href="https://momentumspace.cl/"><b>👉 https://momentumspace.cl/ 👈</b></a>
</p>

</div>

---

## 👨‍💻 Ficha Técnica Institucional y Evaluación Oficial

<table align="center" width="100%">
  <tr>
    <td width="50%"><b>👤 Estudiante:</b> Sebastián Torres Zamorano</td>
    <td width="50%"><b>👨‍🏫 Docente:</b> Marcelo Patricio Alvarado Aravena</td>
  </tr>
  <tr>
    <td><b>🏷️ Sección:</b> AP-N4-C1</td>
    <td><b>📅 Año Académico:</b> 2026</td>
  </tr>
  <tr>
    <td><b>📚 Asignatura:</b> Desarrollo Backend (EVA-2)</td>
    <td><b>🏗️ Proyecto Asignado:</b> N°6 Arriendo de Maquinaria de Construcción</td>
  </tr>
  <tr>
    <td><b>🎯 Ponderación:</b> 25% (70% Defensa Oral • 30% Desarrollo Técnico)</td>
    <td><b>🌐 SaaS Operando en Producción:</b> <a href="https://proyecto-backend.momentumspace.cl/">proyecto-backend.momentumspace.cl</a></td>
  </tr>
</table>

---

## 🌟 Características Destacadas de Nivel Enterprise

- 🌐 **SaaS en Producción Operativa:** Plataforma desplegada y operativa en la nube con dominio propio, conexión HTTPS y soporte multi-dispositivo en [https://proyecto-backend.momentumspace.cl/](https://proyecto-backend.momentumspace.cl/).
- 🛡️ **Autenticación JWT con Claims de Rol (RBAC):** Inyección de `rol` (`EMPRESA_CONSTRUCTORA` vs `EJECUTIVO_ARRIENDOS`), `user_id`, `razon_social` y `nombre_completo` directamente en el token de acceso.
- 📦 **Carro de Arriendo Persistente (Post-Logout):** Relación 1 a 1 en base de datos PostgreSQL. Mantiene los ítems, fechas y cotizaciones calculadas aun al cerrar sesión o cambiar de dispositivo.
- ⚡ **Control Transaccional Atómico (ACID):** Descuento atómico de flota mediante bloqueo pesimista `select_for_update()` al pasar al estado `PAGADO`. Previene condiciones de carrera (*Race Conditions*) y sobre-arriendo.
- 🔄 **Reposición Automática de Flota:** Al transicionar un contrato a `COMPLETADO` (devolución del equipo) o `CANCELADO`, las unidades se reincorporan automáticamente al inventario libre del catálogo.
- 📐 **Modelo Relacional Estrictamente en 3FN:** Desacoplamiento contable mediante snapshots históricos inmutables en `DetalleContratoArriendo` (`tarifa_diaria_congelada`, `monto_garantia_congelado`, `dias_totales`).
- 🔍 **Filtrado Declarativo Avanzado (`django-filter`):** Búsqueda compuesta por categorías, slugs, rangos de precio de tarifa diaria, garantía y disponibilidad real.
- 📑 **Swagger / OpenAPI 3.0 con Header Solo Admin:** Documentación técnica viva con `drf-spectacular` y portal `/documentacion/` con restricción exclusiva de Administrador requerida en pauta académica.
- 🎨 **Interfaz de Usuario Web Industrial:** Templates responsivos con Tailwind CSS, fotografías HD generadas por IA de faena y panel CRUD administrativo.

---

## 🏗️ Diagrama Entidad-Relación en Tercera Forma Normal (3FN)

```mermaid
erDiagram
    USUARIO ||--|| CARRO_ARRIENDO : "1:1 Persistente Post-Logout"
    USUARIO ||--o{ CONTRATO_ARRIENDO : "1:N Cliente Emisor"
    CATEGORIA_EQUIPO ||--o{ MAQUINARIA : "1:N Catálogo Industrial"
    CARRO_ARRIENDO ||--o{ ITEM_CARRO_ARRIENDO : "1:N Líneas del Carro"
    MAQUINARIA ||--o{ ITEM_CARRO_ARRIENDO : "1:N Equipo Solicitado"
    CONTRATO_ARRIENDO ||--o{ DETALLE_CONTRATO : "1:N Snapshot Inmutable 3FN"
    MAQUINARIA ||--o{ DETALLE_CONTRATO : "1:N Referencia de Flota"
    CONTRATO_ARRIENDO ||--o{ HISTORIAL_TRANSICION : "1:N Auditoría de Estados"

    USUARIO {
        int id PK
        string username UK
        string email
        string rol "EMPRESA_CONSTRUCTORA | EJECUTIVO_ARRIENDOS"
        string razon_social
        string rut_empresa
        string telefono
        string direccion_obra
    }

    CATEGORIA_EQUIPO {
        int id PK
        string nombre "Excavadoras, Generadores, Andamios, Hormigoneras"
        string slug UK
        string icono
    }

    MAQUINARIA {
        int id PK
        int categoria_id FK
        string nombre
        string codigo_sku UK
        string marca
        string modelo
        decimal tarifa_diaria
        decimal monto_garantia
        int flota_total
        int flota_disponible
        string estado_operativo "DISPONIBLE | EN_MANTENCION"
        string imagen_url
    }

    CARRO_ARRIENDO {
        int id PK
        int usuario_id FK,UK
        datetime actualizado_en
    }

    ITEM_CARRO_ARRIENDO {
        int id PK
        int carro_id FK
        int maquinaria_id FK
        int cantidad
        date fecha_inicio
        date fecha_fin
    }

    CONTRATO_ARRIENDO {
        int id PK
        int cliente_id FK
        int ejecutivo_aprobador_id FK
        string codigo_contrato UK
        string estado "BORRADOR | PENDIENTE_PAGO | PAGADO | EN_FAENA | COMPLETADO | CANCELADO"
        decimal total_arriendo
        decimal total_garantias
        decimal total_general
        datetime pagado_en
        string direccion_faena
    }

    DETALLE_CONTRATO {
        int id PK
        int contrato_id FK
        int maquinaria_id FK
        int cantidad
        date fecha_inicio
        date fecha_fin
        int dias_totales
        decimal tarifa_diaria_congelada "Snapshot 3FN"
        decimal monto_garantia_congelado "Snapshot 3FN"
        decimal subtotal_arriendo
        decimal subtotal_garantia
    }

    HISTORIAL_TRANSICION {
        int id PK
        int contrato_id FK
        int usuario_ejecutor_id FK
        string estado_anterior
        string estado_nuevo
        datetime fecha_cambio
        string motivo
    }
```

---

## ⚡ Flujo Transaccional Atómico y Concurrencia de Flota

```mermaid
sequenceDiagram
    autonumber
    actor C as Empresa Constructora
    participant API as Checkout View (Atomic)
    participant Lock as PostgreSQL (Row Locking)
    participant Contrato as Modelo Contrato (3FN)
    participant Flota as Inventario Maquinaria
    actor E as Ejecutivo Arriendos

    C->>API: POST /api/contratos-arriendo/checkout/ (Confirmar y Pagar)
    Note over API,Lock: Inicia transaction.atomic()
    API->>Lock: SELECT ... FOR UPDATE (Bloqueo pesimista de filas)
    Lock-->>API: Filas bloqueadas exclusivamente
    API->>Flota: Valida flota_disponible >= cantidad
    alt Stock Insuficiente
        API-->>C: 400 Bad Request: Flota agotada por concurrencia (Rollback)
    else Stock Disponible
        API->>Flota: Descuenta flota_disponible (flota -= cantidad)
        API->>Contrato: Crea Contrato estado PAGADO + Snapshots Detalle
        API->>C: 201 Created: Contrato emitido y flota asegurada (Commit)
    end
    Note over Contrato,Flota: Fin de la transacción atómica

    E->>API: POST /api/contratos-arriendo/{id}/transicionar/ (COMPLETADO)
    API->>Flota: Reposición automática de stock (flota += cantidad)
    API-->>E: 200 OK: Maquinaria reincorporada al catálogo
```

---

## 🚀 Guía de Instalación y Ejecución Local (Para el Profesor)

### 1. Clonar el repositorio
```bash
git clone https://github.com/sebatmail/Arriendo-maquinaria-drf-postgresql.git
cd Arriendo-maquinaria-drf-postgresql
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia el archivo de ejemplo `.env.example` a `.env`:
```bash
cp .env.example .env
```
*(Si no tienes PostgreSQL instalado, el sistema activa automáticamente SQLite con `USE_SQLITE_FALLBACK=True` en `.env`)*.

### 4. Ejecutar migraciones y sembrar datos de prueba
```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Ejecutar suite de pruebas unitarias y de integración
```bash
python manage.py test renting
```
> **Resultado esperado:** 6 de 6 pruebas automatizadas aprobadas al 100% `[OK]`.

### 6. Iniciar servidor de desarrollo
```bash
python manage.py runserver
```
Abre en tu navegador: **`http://127.0.0.1:8000/`**

---

## 🔑 Credenciales de Acceso para Pruebas

| Rol de Usuario | Nombre de Usuario | Contraseña | Permisos y Capacidades |
| :--- | :--- | :--- | :--- |
| **👑 Ejecutivo / Admin** | `admin_ejecutivo` | `admin1234` | CRUD Maquinarias, transición de estados de contratos, Swagger Header Admin. |
| **🏗️ Constructora Demo** | `constructora_demo` | `demo1234` | Catálogo en tiempo real, carro persistente, checkout transaccional y mis contratos. |
| **🏢 Constructora Andes** | `constructora_andes` | `demo1234` | Cuenta secundaria para pruebas de concurrencia y múltiples clientes. |

---

## 🌐 SaaS en Producción en la Web
El sistema completo se encuentra operando de forma continua en producción:
- 🔗 **Plataforma Web SaaS:** [https://proyecto-backend.momentumspace.cl/](https://proyecto-backend.momentumspace.cl/)
- 📑 **Consola Swagger OpenAPI:** [https://proyecto-backend.momentumspace.cl/api/docs/](https://proyecto-backend.momentumspace.cl/api/docs/)
- 📬 **Contacto de Soporte:** storres@momentumspace.cl

---

<div align="center">
  <b>Desarrollado por Sebastián Torres Zamorano • Evaluación Oficial EVA-2 Backend 2026</b>
</div>
