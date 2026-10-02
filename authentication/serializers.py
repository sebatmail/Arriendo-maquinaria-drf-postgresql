"""
================================================================================
SERIALIZADORES DE AUTENTICACIÓN Y JWT CON CLAIMS PERSONALIZADOS
================================================================================
Implementa la inclusión de claims de rol en los tokens JWT (access/refresh)
y el registro estructurado de usuarios con validaciones de seguridad.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

Usuario = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador JWT personalizado que añade claims explícitos en el payload:
    - rol: Rol del usuario en el sistema
    - user_id: ID primario en la base de datos
    - username: Nombre de usuario
    - email: Correo electrónico
    - razon_social: Razón social de la empresa constructora
    - nombre_completo: Nombre y apellido
    - es_ejecutivo: Booleano para verificación rápida en cliente
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Inyección de claims personalizados en el payload del JWT
        token['user_id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['rol'] = user.rol
        token['rol_display'] = user.get_rol_display()
        token['razon_social'] = user.razon_social or ''
        token['nombre_completo'] = user.get_full_name() or user.username
        token['es_ejecutivo'] = user.es_ejecutivo

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Añade metadatos del usuario en la respuesta JSON del endpoint de login
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'rol': self.user.rol,
            'rol_display': self.user.get_rol_display(),
            'razon_social': self.user.razon_social,
            'rut_empresa': self.user.rut_empresa,
            'nombre_completo': self.user.get_full_name() or self.user.username,
            'es_ejecutivo': self.user.es_ejecutivo,
        }
        return data


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para consulta y perfil de usuarios.
    """
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'rol_display', 'rut_empresa', 'razon_social',
            'telefono', 'direccion_obra', 'is_staff', 'date_joined'
        ]
        read_only_fields = ['id', 'is_staff', 'date_joined', 'rol_display']


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para autoregistro seguro de empresas constructoras o ejecutivos.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'rol', 'rut_empresa',
            'razon_social', 'telefono', 'direccion_obra'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas ingresadas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario
