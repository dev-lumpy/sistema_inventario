from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, null=True, blank=True)
    user_name = models.CharField(max_length=50, unique=True)
    correo = models.CharField(max_length=150, unique=True)
    password_hash = models.TextField()
    debe_cambiar_password = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self) -> str:
        return self.user_name


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        primary_key=True,
        db_column="id",
        on_delete=models.CASCADE,
        related_name="administrador",
    )
    nombre_negocio = models.CharField(max_length=150, null=True, blank=True)
    moneda = models.CharField(max_length=3, default="BOB")

    class Meta:
        managed = False
        db_table = "administradores"
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self) -> str:
        return self.nombre_negocio or self.usuario.user_name


class Vendedor(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        primary_key=True,
        db_column="id",
        on_delete=models.CASCADE,
        related_name="vendedor",
    )
    creado_por_admin = models.ForeignKey(
        Administrador,
        db_column="creado_por_admin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendedores_creados",
    )
    creado_en = models.DateTimeField(default=timezone.now)
    bloqueado = models.BooleanField(default=False)
    motivo_bloqueo = models.TextField(null=True, blank=True)
    bloqueado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "vendedores"
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

    def __str__(self) -> str:
        return self.usuario.user_name


class VendedorAdministrador(models.Model):
    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("aceptado", "Aceptado"),
        ("rechazado", "Rechazado"),
        ("inactivo", "Inactivo"),
    )
    SOLICITADO_POR = (
        ("admin", "Administrador"),
        ("vendedor", "Vendedor"),
    )

    pk = models.CompositePrimaryKey("vendedor", "administrador")
    vendedor = models.ForeignKey(
        Vendedor,
        db_column="vendedor_id",
        on_delete=models.CASCADE,
        related_name="vinculos",
    )
    administrador = models.ForeignKey(
        Administrador,
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="vinculos",
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    solicitado_por = models.CharField(max_length=20, choices=SOLICITADO_POR)
    motivo_estado = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "vendedor_administrador"
        verbose_name = "Vínculo vendedor/administrador"
        verbose_name_plural = "Vínculos vendedor/administrador"
