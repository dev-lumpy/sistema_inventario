# apps/usuarios/models.py
import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
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
        constraints = [
            models.CheckConstraint(
                check=Q(email=Lower("email")),
                name="chk_usuarios_usuario_email_lowercase",
            ),
            models.UniqueConstraint(
                Lower("email"),
                name="uniq_usuarios_usuario_email_ci",
            ),
        ]


class AdministradorORM(UsuarioORM):    # ← HIJO 1
    class Meta:
        db_table = "usuarios_administrador"


class VendedorORM(UsuarioORM):         # ← HIJO 2
    admins = models.ManyToManyField(
        AdministradorORM,
        related_name="vendedores",
        blank=True,
    )

    class Meta:
        db_table = "usuarios_vendedor"


class SolicitudAdmin(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_ACEPTADA  = 'aceptada'
    ESTADO_RECHAZADA = 'rechazada'
    ESTADO_BLOQUEADA = 'bloqueada'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ACEPTADA,  'Aceptada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
        (ESTADO_BLOQUEADA, 'Bloqueada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vendedor = models.ForeignKey(
        'usuarios.VendedorORM',
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas',
    )
    administrador = models.ForeignKey(
        'usuarios.AdministradorORM',
        on_delete=models.CASCADE,
        related_name='solicitudes_recibidas',
    )

    mensaje = models.CharField(max_length=200, blank=True)
    respuesta_admin = models.CharField(max_length=200, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios_solicitud_admin'
        ordering = ['-fecha_creacion']
        constraints = [
            models.UniqueConstraint(
                fields=['vendedor', 'administrador'],
                condition=models.Q(estado='pendiente'),
                name='unique_solicitud_pendiente_por_admin',
            ),
        ]

    def __str__(self):
        return f'{self.vendedor.username} → {self.administrador.username} ({self.estado})'
