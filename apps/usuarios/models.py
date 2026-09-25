# apps/usuarios/models.py
import uuid
from django.db import models


class UsuarioORM(models.Model):        # ← PADRE
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
