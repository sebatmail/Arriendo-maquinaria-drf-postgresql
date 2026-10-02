"""
================================================================================
VISTAS DE INTERFAZ WEB (DJANGO TEMPLATES + DRF / JWT INTEGRATION)
================================================================================
Controladores para renderizar la experiencia interactiva de usuario y administración.
Sincroniza el estado de autenticación con sesiones y tokens JWT.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from authentication.models import Usuario, RolUsuario
from renting.models import (
    CategoriaEquipo,
    Maquinaria,
    CarroArriendo,
    ContratoArriendo,
    EstadoContrato,
    EstadoMaquinaria
)
from renting.filters import MaquinariaFilter

def index_catalogo_view(request):
    """
    Vista principal del Catálogo público interactivo con soporte para django-filters.
    """
    queryset = Maquinaria.objects.select_related('categoria').all()
    filtro = MaquinariaFilter(request.GET, queryset=queryset)
    categorias = CategoriaEquipo.objects.all()

    # Obtener contador del carro si el usuario está autenticado
    cantidad_carro = 0
    if request.user.is_authenticated and request.user.rol == RolUsuario.EMPRESA_CONSTRUCTORA:
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        cantidad_carro = carro.cantidad_items

    return render(request, 'web_ui/catalogo.html', {
        'filter': filtro,
        'maquinarias': filtro.qs,
        'categorias': categorias,
        'cantidad_carro': cantidad_carro,
        'categoria_seleccionada': request.GET.get('categoria_slug', ''),
    })


@login_required
def carro_view(request):
    """
    Vista del Carro de Arriendo persistente del cliente.
    """
    if request.user.rol != RolUsuario.EMPRESA_CONSTRUCTORA and not request.user.is_superuser:
        messages.warning(request, 'El carro de arriendo está disponible únicamente para Empresas Constructoras.')
        return redirect('index_catalogo')

    carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
    items = carro.items.select_related('maquinaria__categoria').all()

    return render(request, 'web_ui/carro.html', {
        'carro': carro,
        'items': items,
    })


@login_required
def mis_contratos_view(request):
    """
    Portal de contratos históricos para la Empresa Constructora autenticada.
    """
    if request.user.rol != RolUsuario.EMPRESA_CONSTRUCTORA and not request.user.is_superuser:
        messages.warning(request, 'La sección de Mis Contratos está reservada para Empresas Constructoras.')
        return redirect('index_catalogo')

    contratos = ContratoArriendo.objects.filter(cliente=request.user).prefetch_related('detalles', 'historial_estados').order_by('-creado_en')
    return render(request, 'web_ui/mis_contratos.html', {
        'contratos': contratos,
    })


@login_required
def admin_maquinarias_view(request):
    """
    Panel CRUD de gestión de inventario y flota para Ejecutivos de Arriendo.
    """
    if request.user.rol != RolUsuario.EJECUTIVO_ARRIENDOS and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Esta vista administrativa es exclusiva para Ejecutivos de Arriendo.')
        return redirect('index_catalogo')

    maquinarias = Maquinaria.objects.select_related('categoria').all().order_by('categoria', 'nombre')
    categorias = CategoriaEquipo.objects.all()
    estados_operativos = EstadoMaquinaria.choices

    return render(request, 'web_ui/admin_maquinarias.html', {
        'maquinarias': maquinarias,
        'categorias': categorias,
        'estados_operativos': estados_operativos,
    })


@login_required
def admin_contratos_view(request):
    """
    Consola de transición y control de estados de contratos para Ejecutivos.
    """
    if request.user.rol != RolUsuario.EJECUTIVO_ARRIENDOS and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Acceso denegado: Solo el personal de gestión puede administrar contratos.')
        return redirect('index_catalogo')

    contratos = ContratoArriendo.objects.select_related('cliente').prefetch_related('detalles', 'historial_estados').all().order_by('-creado_en')
    estados_contrato = EstadoContrato.choices

    return render(request, 'web_ui/admin_contratos.html', {
        'contratos': contratos,
        'estados_contrato': estados_contrato,
    })


def login_view(request):
    """
    Inicio de sesión interactivo con sincronización JWT.
    """
    if request.user.is_authenticated:
        return redirect('index_catalogo')

    if request.method == 'POST':
        usuario_nom = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario_nom, password=clave)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.razon_social or user.get_full_name() or user.username}!')
            next_url = request.GET.get('next') or 'index_catalogo'
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas. Por favor verifique su usuario y contraseña.')

    return render(request, 'web_ui/login.html')


def registro_view(request):
    """
    Registro público de Empresas Constructoras.
    """
    if request.user.is_authenticated:
        return redirect('index_catalogo')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        razon_social = request.POST.get('razon_social')
        rut_empresa = request.POST.get('rut_empresa')
        telefono = request.POST.get('telefono')
        direccion_obra = request.POST.get('direccion_obra')
        rol = request.POST.get('rol', RolUsuario.EMPRESA_CONSTRUCTORA)

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'web_ui/registro.html')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está registrado.')
            return render(request, 'web_ui/registro.html')

        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol=rol,
            razon_social=razon_social,
            rut_empresa=rut_empresa,
            telefono=telefono,
            direccion_obra=direccion_obra
        )
        login(request, usuario)
        messages.success(request, 'Registro completado con éxito. Su carro persistente ha sido inicializado.')
        return redirect('index_catalogo')

    return render(request, 'web_ui/registro.html')


def logout_view(request):
    """
    Cierre de sesión seguro.
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente. Su carro de arriendo se mantiene persistido en PostgreSQL.')
    return redirect('index_catalogo')


def documentacion_admin_view(request):
    """
    Vista de documentación Swagger/OpenAPI con validación de rol de Admin (Requerimiento Pizarra).
    """
    if not request.user.is_authenticated or (request.user.rol != RolUsuario.EJECUTIVO_ARRIENDOS and not request.user.is_staff and not request.user.is_superuser):
        messages.warning(request, 'Acceso restringido: La documentación OpenAPI/Swagger es visible exclusivamente para el rol Administrador/Ejecutivo.')
        return redirect('login')

    return render(request, 'web_ui/documentacion_admin.html')
