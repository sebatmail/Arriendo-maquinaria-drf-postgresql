"""
Generador de Documento PDF de Alta Calidad para la Defensa Oral EVA-2
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "RENT-EQUIP PRO | Guía de Defensa Oral y Banco de Respuestas Técnicas EVA-2")
            self.drawRightString(612 - 54, 750, "Proyecto 6: Arriendo de Maquinaria")
            self.setStrokeColor(HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Footer
        self.setStrokeColor(HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        
        footer_text = "Estudiante: Sebastián Torres Zamorano | Sección: Backend DLY01 | Año: 2026 | Arquitectura 3FN + DRF + PostgreSQL"
        self.drawString(54, 32, footer_text)
        self.drawRightString(612 - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def generar_pdf(filename="DEFENSA_ORAL_Y_PREGUNTAS_EXAMEN_EVA2.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = HexColor("#0f172a") # Slate 900
    accent_color = HexColor("#d97706")  # Amber 600
    sub_color = HexColor("#0369a1")     # Sky 700
    dark_text = HexColor("#1e293b")
    code_bg = HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=HexColor("#b45309"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=HexColor("#0f172a"),
        backColor=code_bg,
        spaceBefore=4,
        spaceAfter=6
    )

    badge_style = ParagraphStyle(
        'Badge',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=HexColor("#ffffff")
    )

    story = []

    # =========================================================================
    # PORTADA / ENCABEZADO INSTITUCIONAL
    # =========================================================================
    header_data = [
        [
            Paragraph("<b>EVALUACIÓN EVA-2: DESARROLLO BACKEND</b><br/><font size=8 color='#64748b'>GUÍA MAESTRA DE DEFENSA ORAL Y BANCO DE PREGUNTAS (70 PUNTOS / 70%)</font>", styles['Normal']),
            Paragraph("<b>CALIFICACIÓN ESPERADA: 100%</b><br/><font size=8 color='#16a34a'>ESTÁNDAR TOP 1% ENTERPRISE</font>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold', fontSize=9, textColor=HexColor("#16a34a")))
        ]
    ]
    t_header = Table(header_data, colWidths=[330, 174])
    t_header.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, accent_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 15))

    story.append(Paragraph("RENT-EQUIP PRO: Arriendo de Maquinaria Pesada", title_style))
    story.append(Paragraph("Proyecto 6 (Renting / Servicios) • Arquitectura Django REST Framework + PostgreSQL + 3FN", subtitle_style))

    # Ficha Técnica Table
    ficha_data = [
        [Paragraph("<b>Estudiante:</b>", answer_style), Paragraph("Sebastián Torres Zamorano", answer_style), Paragraph("<b>Asignatura:</b>", answer_style), Paragraph("Desarrollo Backend (EVA-2)", answer_style)],
        [Paragraph("<b>Sección:</b>", answer_style), Paragraph("Backend DLY01", answer_style), Paragraph("<b>Ponderación:</b>", answer_style), Paragraph("25% Total (70% Defensa Oral)", answer_style)],
        [Paragraph("<b>Motor DB:</b>", answer_style), Paragraph("PostgreSQL (3FN Relacional)", answer_style), Paragraph("<b>Seguridad:</b>", answer_style), Paragraph("JWT Claims RBAC + ACID Trans.", answer_style)],
    ]
    t_ficha = Table(ficha_data, colWidths=[75, 175, 80, 174])
    t_ficha.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ficha)
    story.append(Spacer(1, 15))

    # =========================================================================
    # SECCIÓN 1: DOMINIO DE LA ARQUITECTURA, BD Y MODELOS 3FN (12 PTS)
    # =========================================================================
    story.append(Paragraph("1. Dominio de la Arquitectura, Configuración DB y Modelos (12 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P1.1: ¿Por qué este modelo de datos cumple con la Tercera Forma Normal (3FN)? Justifique técnicamente.", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Una base de datos está en 3FN si está en 2FN y <b>ningún atributo no clave depende transitivamente de la clave primaria</b> (X &rarr; Y no transitivo). En nuestro sistema:<br/>"
        "1. <b>1FN:</b> Cada campo es atómico (sin listas serializadas dentro de celdas), y existen claves primarias definidas.<br/>"
        "2. <b>2FN:</b> Todos los atributos no clave dependen funcionalmente de la clave primaria completa de cada tabla.<br/>"
        "3. <b>3FN:</b> Desacoplamos las tarifas del catálogo mutable respecto al contrato histórico. La tabla <code>DetalleContratoArriendo</code> congela los valores (<code>tarifa_diaria_congelada</code>, <code>monto_garantia_congelado</code>, <code>dias_totales</code>). Esto garantiza que si el administrador modifica mañana el precio de catálogo de una Excavadora CAT, los contratos previamente firmados y pagados no sufran alteraciones no autorizadas ni dependencias transitivas corruptas.",
        answer_style
    ))

    story.append(Paragraph("P1.2: ¿Cómo se configura PostgreSQL en Django y qué ventajas aporta en este proyecto?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> En <code>config/settings.py</code> se define el motor nativo <code>django.db.backends.postgresql</code> conectado a la base de datos <code>arriendo_maquinaria_db</code> mediante las librerías <code>psycopg2-binary</code> o <code>psycopg</code> (v3).<br/>"
        "<b>Ventaja Crítica:</b> A diferencia de SQLite (que bloquea todo el archivo en escrituras concurrentes), PostgreSQL soporta <b>bloqueo a nivel de fila (Row-Level Locking)</b> mediante <code>SELECT ... FOR UPDATE</code>. Esto permite que múltiples empresas constructoras hagan reservas simultáneas sin provocar condiciones de carrera ni sobre-arriendo de unidades físicas de la flota.",
        answer_style
    ))

    story.append(Paragraph("P1.3: ¿Dónde y por qué se implementan los atributos explícitos con CHOICES?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Se implementaron enumeraciones tipadas usando <code>models.TextChoices</code> en tres entidades clave:<br/>"
        "• <code>RolUsuario.choices</code>: <code>EMPRESA_CONSTRUCTORA</code> vs <code>EJECUTIVO_ARRIENDOS</code>.<br/>"
        "• <code>EstadoContrato.choices</code>: <code>PENDIENTE</code>, <code>PAGADO</code>, <code>ENTREGADO</code>, <code>COMPLETADO</code>, <code>CANCELADO</code>.<br/>"
        "• <code>EstadoMaquinaria.choices</code>: <code>DISPONIBLE</code>, <code>MANTENCION</code>, <code>DE_BAJA</code>.<br/>"
        "Esto asegura integridad de dominio a nivel de ORM y de base de datos, evitando strings arbitrarios y facilitando la documentación OpenAPI automática.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 2: DEFENSA DEL FLUJO JWT, CLAIMS DE ROL Y RBAC (12 PTS)
    # =========================================================================
    story.append(Paragraph("2. Flujo de Autenticación JWT, Claims de Rol y Permisos RBAC (12 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P2.1: Explique el ciclo de vida del JWT y cómo se inyectan los claims personalizados.", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> El usuario envía sus credenciales a <code>POST /api/auth/login/</code>. La clase <code>CustomTokenObtainPairSerializer</code> hereda de <code>TokenObtainPairSerializer</code> de SimpleJWT y sobreescribe el método de clase <code>get_token(cls, user)</code>:<br/>"
        "<code>token['user_id'] = user.id</code><br/>"
        "<code>token['rol'] = user.rol  # 'EMPRESA_CONSTRUCTORA' o 'EJECUTIVO_ARRIENDOS'</code><br/>"
        "<code>token['razon_social'] = user.razon_social</code><br/>"
        "El cliente recibe un <b>Access Token</b> (vida útil de 8 horas) y un <b>Refresh Token</b> (7 días con rotación y token blacklist). Al enviar solicitudes protegidas, el cliente incluye el header <code>Authorization: Bearer &lt;access_token&gt;</code>.",
        answer_style
    ))

    story.append(Paragraph("P2.2: ¿Cómo se aplican las restricciones de permisos RBAC en los endpoints?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Creamos clases de permisos personalizadas que heredan de <code>rest_framework.permissions.BasePermission</code>:<br/>"
        "• <code>IsEmpresaConstructora</code>: Valida <code>request.user.rol == 'EMPRESA_CONSTRUCTORA'</code>. Protege el carro de arriendos, el checkout y mis-contratos.<br/>"
        "• <code>IsEjecutivoArriendos</code>: Valida <code>request.user.rol == 'EJECUTIVO_ARRIENDOS'</code> o <code>is_staff</code>. Protege la mutación de catálogo y la transición de estados de contratos.<br/>"
        "• <code>IsAdminOrReadOnly</code>: Permite safe methods (<code>GET</code>) a todo público y restringe escrituras a ejecutivos.<br/>"
        "• <code>IsDocAdminUser</code>: Cumple con el requerimiento de clase restringiendo Swagger al rol de Administrador.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 3: CARRO DE ARRIENDO PERSISTENTE POST-LOGOUT (12 PTS)
    # =========================================================================
    story.append(Paragraph("3. Persistencia del Carro de Compras Post-Logout (12 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P3.1: ¿Cómo se garantiza que el carro persista tras cerrar sesión o cambiar de PC?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> El carro <b>no reside en cookies ni en localStorage</b>. Está modelado en PostgreSQL mediante la entidad <code>CarroArriendo</code> que mantiene una relación <code>OneToOneField(Usuario, related_name='carro_activo')</code> y una relación 1 a N con <code>ItemCarroArriendo</code>. Cada ítem almacena la maquinaria FK, cantidad, fecha de inicio y fecha de fin.<br/>"
        "Al hacer logout o conectarse desde otro dispositivo móvil o navegador, la autenticación JWT consulta el registro persistido del usuario en la base de datos, recuperando íntegramente los ítems y las cotizaciones en tiempo real.",
        answer_style
    ))

    story.append(Paragraph("P3.2: ¿Por qué el inventario NO se descuenta al agregar un ítem al carro?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Descontar stock al agregar al carro provocaría <i>ataques de denegación de inventario (Cart Abandonment Stock Hijacking)</i>, donde un usuario malicioso llena su carro sin pagar bloqueando la flota para clientes reales. Por regla de negocio y rúbrica EVA-2, el carro solo almacena la intención de arriendo; el descuento ocurre de forma atómica y estricta en el momento del <b>Checkout y Pago Confirmado</b>.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 4: CICLO TRANSACCIONAL ATÓMICO, CHECKOUT Y STOCK (12 PTS)
    # =========================================================================
    story.append(Paragraph("4. Ciclo Transaccional Atómico, Checkout y Gestión de Flota (12 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P4.1: Explique la ejecución de la transacción atómica en el Checkout (`POST /api/contratos/checkout/`).", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Se encapsula la lógica dentro del context manager <code>with transaction.atomic():</code> de Django:<br/>"
        "1. <b>Bloqueo Pesimista:</b> Se ejecuta <code>Maquinaria.objects.select_for_update().filter(id__in=maquinarias_ids)</code> para bloquear las filas en PostgreSQL.<br/>"
        "2. <b>Validación de Disponibilidad:</b> Se comprueba <code>flota_disponible &gt;= item.cantidad</code> y <code>estado_operativo == 'DISPONIBLE'</code>.<br/>"
        "3. <b>Descuento Atómico:</b> Se resta <code>maq.flota_disponible -= item.cantidad</code> y se ejecuta <code>maq.save(update_fields=['flota_disponible'])</code>.<br/>"
        "4. <b>Creación de Contrato:</b> Se genera el <code>ContratoArriendo</code> en estado <code>PAGADO</code> y los <code>DetalleContratoArriendo</code> congelando precios y fechas.<br/>"
        "5. <b>Vaciado de Carro y Auditoría:</b> Se limpia el carro activo y se registra en <code>HistorialTransicionContrato</code>.<br/>"
        "Si ocurre cualquier falla o stock insuficiente, se lanza una excepción y la base de datos realiza un <b>ROLLBACK automático</b>, dejando los saldos intactos.",
        answer_style
    ))

    story.append(Paragraph("P4.2: ¿Cómo opera la reposición automática de flota al transicionar a COMPLETADO o CANCELADO?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> En la vista <code>AdminActualizarEstadoContratoView</code> (exclusiva de Ejecutivos), al recibir un PATCH con estado <code>COMPLETADO</code> (devolución del equipo por la constructora) o <code>CANCELADO</code>, el sistema itera sobre los detalles del contrato y reincorpora las unidades con bloqueo atómico:<br/>"
        "<code>maq.flota_disponible = min(maq.flota_total, maq.flota_disponible + detalle.cantidad)</code><br/>"
        "Esto restituye la maquinaria al catálogo público en tiempo real para que otras empresas puedan arrendarla de inmediato.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 5: FILTROS, BÚSQUEDA Y OPENAPI / SWAGGER (10 PTS)
    # =========================================================================
    story.append(Paragraph("5. Filtros, Búsquedas y Documentación OpenAPI / Swagger (10 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P5.1: ¿Cómo está implementado `django-filter` y qué parámetros acepta?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Se construyó la clase <code>MaquinariaFilter(django_filters.FilterSet)</code> vinculada a <code>MaquinariaViewSet</code> a través de <code>filterset_class</code> y <code>DjangoFilterBackend</code>. Acepta:<br/>"
        "• <code>categoria</code> (FK) y <code>categoria_slug</code> (exact/iexact).<br/>"
        "• <code>min_precio</code> y <code>max_precio</code> (rango sobre <code>tarifa_diaria</code> con <code>gte</code> / <code>lte</code>).<br/>"
        "• <code>solo_disponibles=true</code> (filtro booleano que comprueba <code>flota_disponible &gt; 0</code>).<br/>"
        "• <code>q</code> (búsqueda de texto sobre nombre, SKU, marca, modelo y descripción).",
        answer_style
    ))

    story.append(Paragraph("P5.2: ¿Cómo se generó la documentación Swagger y por qué está restringida?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Se utilizó <code>drf-spectacular</code> configurado con esquema OpenAPI 3.0. Expone los endpoints <code>/api/schema/</code>, <code>/api/docs/</code> (Swagger UI) y <code>/api/redoc/</code>. Cada endpoint cuenta con decoradores <code>@extend_schema</code> con descripción, tags y códigos de respuesta.<br/>"
        "Siguiendo la instrucción del docente en clase (<i>'header solo admin'</i>), la vista de documentación incluye un banner/control de acceso verificado para el rol Ejecutivo/Administrador.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 6: CÓDIGO LIMPIO, COMENTARIOS Y FOOTER (12 PTS)
    # =========================================================================
    story.append(Paragraph("6. Calidad de Código, Comentarios en Bloques y Footer Base (12 Puntos)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("P6.1: ¿Cómo se asegura la renderización global del Footer con datos del estudiante?", question_style))
    story.append(Paragraph(
        "<b>Respuesta Senior:</b> Se creó un <b>Context Processor personalizado</b> en <code>web_ui/context_processors.py</code> llamado <code>evaluacion_footer_info</code>, registrado en <code>settings.py</code> dentro de <code>TEMPLATES['OPTIONS']['context_processors']</code>.<br/>"
        "Esto inyecta automáticamente el diccionario <code>alumno_info</code> (Nombre: <b>Sebastián Torres Zamorano</b>, Sección: <b>Backend DLY01</b>, Año: <b>2026</b>) en todas las vistas HTML del sistema sin ensuciar la lógica de los controladores.",
        answer_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 7: MARKETING & ESCALABILIDAD INDUSTRIAL (€100.000+ SAAS)
    # =========================================================================
    story.append(Paragraph("7. Visión Estratégica: Marketing y Escalabilidad B2B SaaS (€100.000+)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph(
        "Para posicionar esta plataforma en el <b>1% superior de la industria tecnológica de Renting</b> y justificar una valoración sobre los 100.000 Euros, se diseñó la siguiente arquitectura de escalamiento comercial:<br/>"
        "1. <b>Modelo de Monetización B2B Dual:</b><br/>"
        "   • <i>Take-Rate por Transacción (5% - 8%):</i> Comisión sobre cada arriendo generado por empresas asociadas.<br/>"
        "   • <i>Suscripción SaaS Enterprise (€299 - €999/mes):</i> Para constructoras con módulos avanzados de gestión de faena multi-obra.<br/>"
        "2. <b>Telemetría e Integración IoT:</b> Conexión API vía MQTT / Webhooks con computadores a bordo de maquinaria CAT y Cummins para sincronizar horómetros en tiempo real y alertas de mantención predictiva preventiva.<br/>"
        "3. <b>Fintech & Garantías Digitales (Smart Escrow):</b> Sustitución de boletas de garantía bancarias físicas por pólizas de caución digitales integradas con pasarelas de pago B2B (Transbank Webpay Plus, Stripe B2B).<br/>"
        "4. <b>Arquitectura Cloud Nativa:</b> Soporte para réplicas de lectura en PostgreSQL, caché Redis y despliegue en Kubernetes (EKS / GKE) con alta disponibilidad del 99.99%.",
        answer_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {filename}")

if __name__ == "__main__":
    generar_pdf()
