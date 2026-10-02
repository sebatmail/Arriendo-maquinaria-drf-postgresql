"""
================================================================================
VISTAS DE AUTENTICACIÓN Y CONTROL DE ACCESO (DRF)
================================================================================
Endpoints para autenticación JWT, emisión de tokens con claims de rol,
registro de nuevas cuentas y consulta de perfil.
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer,
    RegistroUsuarioSerializer
)

Usuario = get_user_model()

@extend_schema(
    tags=['Autenticación y Roles'],
    summary='Obtener Token JWT con Claims de Rol',
    description='Autentica credenciales y emite tokens de acceso (Access) y refresco (Refresh) con el rol del usuario inyectado en el payload.'
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Autenticación y Roles'],
    summary='Refrescar Token JWT',
    description='Permite renovar el token de acceso mediante el token de refresco válido.'
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=['Autenticación y Roles'],
    summary='Registro de Nuevo Usuario / Constructora',
    description='Permite registrar una nueva empresa constructora o ejecutivo en la plataforma.',
    responses={201: UsuarioSerializer}
)
class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        user_data = UsuarioSerializer(usuario).data
        return Response(
            {
                'mensaje': 'Usuario registrado exitosamente en el sistema de Renting.',
                'usuario': user_data
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['Autenticación y Roles'],
    summary='Perfil del Usuario Autenticado',
    description='Devuelve los datos del usuario actual autenticado mediante el token JWT.',
    responses={200: UsuarioSerializer}
)
class PerfilUsuarioView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
