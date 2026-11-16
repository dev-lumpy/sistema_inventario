# apps/usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

from .models import (
    AdministradorORM,
    SolicitudAdmin,
    UsuarioORM,
    VendedorORM,
)

User = get_user_model()


class VendedorSerializer(serializers.ModelSerializer):
    # Campos heredados de UsuarioORM (MTI → vienen del padre)
    username = serializers.CharField(source="usuarioorm_ptr.username", read_only=True)
    email = serializers.EmailField(source="usuarioorm_ptr.email", read_only=True)
    activo = serializers.CharField(source="usuarioorm_ptr.activo", read_only=True)
    fecha_creacion = serializers.DateTimeField(source="usuarioorm_ptr.fecha_creacion", read_only=True)
    class Meta:
        model = VendedorORM
        fields = [
            "uuid",              # pk heredada
            "username",
            "email",
            "activo",
            "fecha_creacion",
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioORM
        fields = [
            "uuid",
            "username",
            "email",
            "activo",
            "fecha_creacion",
        ]
        read_only_fields = ["uuid", "fecha_creacion"]



class VendedorResumenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuarioorm_ptr.username", read_only=True)
    email = serializers.EmailField(source="usuarioorm_ptr.email", read_only=True)

    class Meta:
        model = VendedorORM
        fields = ["uuid", "username", "email"]


class AdministradorResumenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuarioorm_ptr.username", read_only=True)
    email = serializers.EmailField(source="usuarioorm_ptr.email", read_only=True)

    class Meta:
        model = AdministradorORM
        fields = ["uuid", "username", "email"]


class SolicitudAdminSerializer(serializers.ModelSerializer):
    vendedor = VendedorResumenSerializer(read_only=True)
    administrador = AdministradorResumenSerializer(read_only=True)

    class Meta:
        model = SolicitudAdmin
        fields = [
            "id",
            "vendedor",
            "administrador",
            "mensaje",
            "respuesta_admin",
            "estado",
            "fecha_creacion",
            "fecha_respuesta",
        ]
        read_only_fields = [
            "id",
            "mensaje",
            "estado",
            "fecha_creacion",
            "fecha_respuesta",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get('request')
        email = attrs['email'].lower().strip()
        password = attrs['password']

        # Autenticación por email (porque USERNAME_FIELD es 'username')
        user_obj = User.objects.filter(email=email).first()
        if user_obj is None or not user_obj.check_password(password):
            raise serializers.ValidationError({
                'detail': 'Email o contraseña incorrectos.',
                'code': 'credenciales_invalidas',
            })


        attrs['user'] = user_obj
        return attrs
