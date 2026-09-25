# infrastructure/repositories/usuario_repository.py
"""Adaptador Django para el repositorio de Usuario (2 tablas)."""

from __future__ import annotations

from typing import Optional

from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.value_objects import (
    EstadoUsuario,
    UsuarioId,
    Email,
    NombreUsuario,
    PasswordHash,
    RolUser
)
from core.domain.usuario.usuario import Usuario
from core.domain.shared.fecha import Fecha

from apps.usuarios.models import (
    AdministradorORM,
    VendedorORM,
)


class DjangoUsuarioRepository(UsuarioRepository):
    """Implementación con Django ORM del repositorio de Usuario."""

    # ------------------------------------------------------------------
    # ESCRITURA
    # ------------------------------------------------------------------


    def guardar_administrador(self, usuario: Usuario) -> None:
        AdministradorORM.objects.update_or_create(
            uuid=usuario.id.valor,
            defaults={
                "username": usuario.nombre.valor,
                "email": usuario.email.valor,
                "password": usuario.password_hash.valor,
                "activo": usuario.activo.valor,
            },
        )

    def guardar_vendedor_con_admin(
        self, vendedor: Usuario, admin_id: UsuarioId
    ) -> None:
        admin_orm = AdministradorORM.objects.get(uuid=admin_id.valor)

        VendedorORM.objects.update_or_create(
            uuid=vendedor.id.valor,
            defaults={
                "username": vendedor.nombre.valor,
                "email": vendedor.email.valor,
                "password": vendedor.password_hash.valor,
                "activo": vendedor.activo.valor,
                "admin": admin_orm,
            },
        )

    # ------------------------------------------------------------------
    # LECTURA
    # ------------------------------------------------------------------

    def obtener_por_id(self, id: UsuarioId) -> Optional[Usuario]:
        # 1) intenta admin
        admin = AdministradorORM.objects.filter(uuid=id.valor).first()
        if admin:
            return self._admin_to_domain(admin)

        # 2) intenta vendedor
        vendedor = (
            VendedorORM.objects
            .select_related("admin")
            .filter(uuid=id.valor)
            .first()
        )
        if vendedor:
            return self._vendedor_to_domain(vendedor)

        return None

    def obtener_por_email(self, email: Email) -> Optional[Usuario]:
        admin = AdministradorORM.objects.filter(email=email.valor).first()
        if admin:
            return self._admin_to_domain(admin)

        vendedor = (
            VendedorORM.objects
            .select_related("admin")
            .filter(email=email.valor)
            .first()
        )
        if vendedor:
            return self._vendedor_to_domain(vendedor)

        return None

    def listar_todos(self) -> list[Usuario]:
        admins = [self._admin_to_domain(a) for a in AdministradorORM.objects.all()]
        vendedores = [
            self._vendedor_to_domain(v)
            for v in VendedorORM.objects.select_related("admin").all()
        ]
        return admins + vendedores

    def obtener_administradores(self) -> list[Usuario]:
        return [
            self._admin_to_domain(a)
            for a in AdministradorORM.objects.filter(activo="activo")
        ]

    # ------------------------------------------------------------------
    # BORRADO
    # ------------------------------------------------------------------

    def eliminar(self, id: UsuarioId) -> None:
        # elimina de la tabla que corresponda
        AdministradorORM.objects.filter(uuid=id.valor).delete()
        VendedorORM.objects.filter(uuid=id.valor).delete()

    # ------------------------------------------------------------------
    # MAPPERS (ORM → Dominio)
    # ------------------------------------------------------------------

    @staticmethod
    def _admin_to_domain(orm: AdministradorORM) -> Usuario:
        return Usuario(
            id=UsuarioId(orm.uuid),
            nombre=NombreUsuario(orm.username),
            email=Email(orm.email),
            password_hash=PasswordHash(orm.password),
            rol=RolUser(RolUser.ADMINISTRADOR),
            activo=EstadoUsuario(orm.activo),
            fecha_creacion=Fecha(orm.fecha_creacion),
        )

    @staticmethod
    def _vendedor_to_domain(orm: VendedorORM) -> Usuario:
        return Usuario(
            id=UsuarioId(orm.uuid),
            nombre=NombreUsuario(orm.username),
            email=Email(orm.email),
            password_hash=PasswordHash(orm.password),
            rol=RolUser(RolUser.VENDEDOR),
            activo=EstadoUsuario(orm.activo),
            fecha_creacion=Fecha(orm.fecha_creacion),
        )

 
