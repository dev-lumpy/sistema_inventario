# apps/usuarios/serializers.py
from rest_framework import serializers
from .models import VendedorORM, UsuarioORM


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
