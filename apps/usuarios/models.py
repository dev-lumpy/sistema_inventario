# apps/usuarios/models.py
import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UsuarioORM(AbstractBaseUser, PermissionsMixin, models.Model):        # ← PADRE
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # El activo solo puede ser 3 estados
    activo = models.CharField(
        max_length=20,
        choices=[("pendiente", "Pendiente"), ("activo", "Activo"), ("inactivo", "Inactivo")],
        default="activo",
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    @property
    def rol(self):
        # Busca el subtipo manualmente
        if AdministradorORM.objects.filter(pk=self.pk).exists():
            return "administrador"
        if VendedorORM.objects.filter(pk=self.pk).exists():
            return "vendedor"
        return "usuario"

    class Meta:
        db_table = "usuarios_usuario"


class AdministradorORM(UsuarioORM):    # ← HIJO 1
    class Meta:
        db_table = "usuarios_administrador"


class VendedorORM(UsuarioORM):         # ← HIJO 2
    admin = models.ForeignKey(
        AdministradorORM,
        on_delete=models.PROTECT,
        related_name="vendedores",
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "usuarios_vendedor"
