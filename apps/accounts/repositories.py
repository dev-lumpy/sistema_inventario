from __future__ import annotations

from core.application.ports.accounts import (
    AdministradorRepository,
    UsuarioRepository,
    VendedorRepository,
    VinculoRepository,
)
from core.domain.accounts.entities import (
    Administrador,
    Usuario,
    Vendedor,
    VinculoVendedorAdministrador,
)
from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.accounts.value_objects import (
    Apellidos,
    Correo,
    Nombre,
    NombreNegocio,
    PasswordHash,
    UserName,
)

from apps.accounts.models import (
    Administrador as AdministradorORM,
    Usuario as UsuarioORM,
    Vendedor as VendedorORM,
    VendedorAdministrador as VinculoORM,
)


def _usuario_to_domain(orm: UsuarioORM) -> Usuario:
    return Usuario(
        id=orm.id,
        nombre=Nombre(orm.nombre),
        apellidos=Apellidos(orm.apellidos),
        user_name=UserName(orm.user_name),
        correo=Correo(orm.correo),
        password_hash=PasswordHash(orm.password_hash),
        debe_cambiar_password=orm.debe_cambiar_password,
        activo=orm.activo,
        creado_en=orm.creado_en,
    )


def _usuario_defaults(usuario: Usuario) -> dict:
    return {
        "nombre": usuario.nombre.valor,
        "apellidos": usuario.apellidos.valor,
        "user_name": usuario.user_name.valor,
        "correo": usuario.correo.valor,
        "password_hash": usuario.password_hash.valor,
        "debe_cambiar_password": usuario.debe_cambiar_password,
        "activo": usuario.activo,
        "creado_en": usuario.creado_en,
    }


class DjangoUsuarioRepository(UsuarioRepository):
    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        orm = UsuarioORM.objects.filter(pk=usuario_id).first()
        return _usuario_to_domain(orm) if orm else None

    def obtener_por_user_name(self, user_name: str) -> Usuario | None:
        orm = UsuarioORM.objects.filter(user_name__iexact=user_name).first()
        return _usuario_to_domain(orm) if orm else None

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        orm = UsuarioORM.objects.filter(correo__iexact=correo).first()
        return _usuario_to_domain(orm) if orm else None

    def obtener_por_nombre(self, nombre: str) -> Usuario | None:
        orm = UsuarioORM.objects.filter(nombre__iexact=nombre).first()
        return _usuario_to_domain(orm) if orm else None

    def guardar(self, usuario: Usuario) -> Usuario:
        if usuario.id is None:
            orm = UsuarioORM.objects.create(**_usuario_defaults(usuario))
        else:
            UsuarioORM.objects.filter(pk=usuario.id).update(**_usuario_defaults(usuario))
            orm = UsuarioORM.objects.get(pk=usuario.id)
        usuario.id = orm.id
        usuario.creado_en = orm.creado_en
        return usuario

    def listar(self) -> list[Usuario]:
        return [_usuario_to_domain(orm) for orm in UsuarioORM.objects.order_by("id")]

    def eliminar(self, usuario_id: int) -> None:
        UsuarioORM.objects.filter(pk=usuario_id).delete()


class DjangoAdministradorRepository(AdministradorRepository):
    def __init__(self, usuario_repo: UsuarioRepository | None = None) -> None:
        self._usuario_repo = usuario_repo or DjangoUsuarioRepository()

    def obtener_por_id(self, administrador_id: int) -> Administrador | None:
        orm = (
            AdministradorORM.objects.select_related("usuario")
            .filter(pk=administrador_id)
            .first()
        )
        if orm is None:
            return None
        return Administrador(
            usuario=_usuario_to_domain(orm.usuario),
            nombre_negocio=NombreNegocio(orm.nombre_negocio),
        )

    def guardar(self, administrador: Administrador) -> Administrador:
        self._usuario_repo.guardar(administrador.usuario)
        AdministradorORM.objects.update_or_create(
            usuario_id=administrador.usuario.id,
            defaults={"nombre_negocio": administrador.nombre_negocio.valor},
        )
        return administrador

    def listar(self) -> list[Administrador]:
        return [
            self.obtener_por_id(orm.pk)  # type: ignore[list-item]
            for orm in AdministradorORM.objects.order_by("usuario_id")
        ]


class DjangoVendedorRepository(VendedorRepository):
    def __init__(self, usuario_repo: UsuarioRepository | None = None) -> None:
        self._usuario_repo = usuario_repo or DjangoUsuarioRepository()

    def obtener_por_id(self, vendedor_id: int) -> Vendedor | None:
        orm = (
            VendedorORM.objects.select_related("usuario")
            .filter(pk=vendedor_id)
            .first()
        )
        if orm is None:
            return None
        return Vendedor(
            usuario=_usuario_to_domain(orm.usuario),
            creado_por_admin_id=orm.creado_por_admin_id,
            creado_en=orm.creado_en,
            bloqueado=orm.bloqueado,
            motivo_bloqueo=orm.motivo_bloqueo,
            bloqueado_en=orm.bloqueado_en,
        )

    def guardar(self, vendedor: Vendedor) -> Vendedor:
        self._usuario_repo.guardar(vendedor.usuario)
        VendedorORM.objects.update_or_create(
            usuario_id=vendedor.usuario.id,
            defaults={
                "creado_por_admin_id": vendedor.creado_por_admin_id,
                "creado_en": vendedor.creado_en,
                "bloqueado": vendedor.bloqueado,
                "motivo_bloqueo": vendedor.motivo_bloqueo,
                "bloqueado_en": vendedor.bloqueado_en,
            },
        )
        return vendedor

    def listar_por_administrador(self, administrador_id: int) -> list[Vendedor]:
        ids = (
            VinculoORM.objects.filter(administrador_id=administrador_id)
            .exclude(vendedor_id=administrador_id)
            .values_list("vendedor_id", flat=True)
            .distinct()
        )
        return [
            self.obtener_por_id(vendedor_id)  # type: ignore[list-item]
            for vendedor_id in ids
        ]


class DjangoVinculoRepository(VinculoRepository):
    def obtener(
        self, vendedor_id: int, administrador_id: int
    ) -> VinculoVendedorAdministrador | None:
        orm = VinculoORM.objects.filter(
            vendedor_id=vendedor_id,
            administrador_id=administrador_id,
        ).first()
        return self._to_domain(orm) if orm else None

    def guardar(
        self, vinculo: VinculoVendedorAdministrador
    ) -> VinculoVendedorAdministrador:
        VinculoORM.objects.update_or_create(
            vendedor_id=vinculo.vendedor_id,
            administrador_id=vinculo.administrador_id,
            defaults={
                "estado": vinculo.estado.value,
                "solicitado_por": vinculo.solicitado_por.value,
                "motivo_estado": vinculo.motivo_estado,
                "creado_en": vinculo.creado_en,
                "actualizado_en": vinculo.actualizado_en,
            },
        )
        return vinculo

    def listar_por_administrador(
        self, administrador_id: int, estado: EstadoVinculo | None = None
    ) -> list[VinculoVendedorAdministrador]:
        qs = VinculoORM.objects.filter(administrador_id=administrador_id)
        if estado is not None:
            qs = qs.filter(estado=estado.value)
        return [self._to_domain(orm) for orm in qs.order_by("-creado_en")]

    def listar_por_vendedor(
        self, vendedor_id: int
    ) -> list[VinculoVendedorAdministrador]:
        qs = VinculoORM.objects.filter(vendedor_id=vendedor_id).order_by("-creado_en")
        return [self._to_domain(orm) for orm in qs]

    def eliminar(self, vendedor_id: int, administrador_id: int) -> None:
        VinculoORM.objects.filter(
            vendedor_id=vendedor_id,
            administrador_id=administrador_id,
        ).delete()

    @staticmethod
    def _to_domain(orm: VinculoORM) -> VinculoVendedorAdministrador:
        return VinculoVendedorAdministrador(
            vendedor_id=orm.vendedor_id,
            administrador_id=orm.administrador_id,
            estado=EstadoVinculo(orm.estado),
            solicitado_por=SolicitadoPor(orm.solicitado_por),
            motivo_estado=orm.motivo_estado,
            creado_en=orm.creado_en,
            actualizado_en=orm.actualizado_en,
        )
