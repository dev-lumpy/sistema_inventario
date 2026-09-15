"""Entidad Usuario (Aggregate Root)"""

from __future__ import annotations

from core.domain.usuario.value_objects import (
    UsuarioId,
    Email,
    NombreUsuario,
    PasswordHash,
)
from core.domain.usuario.rol import Rol
from core.domain.usuario.exceptions import PermisoDenegadoException
from core.domain.shared.fecha import Fecha


class Usuario:
    """Entidad raíz del agregado Usuario"""

    def __init__(
        self,
        id: UsuarioId,
        nombre: NombreUsuario,
        email: Email,
        password_hash: PasswordHash,
        rol: Rol = Rol.VENDEDOR,
        activo: bool = True,
        fecha_creacion: Fecha | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo
        self.fecha_creacion = fecha_creacion or Fecha.ahora()

    def puede_configurar(self) -> bool:
        """RF-11: Solo ADMINISTRADOR puede configurar"""
        return self.rol == Rol.ADMINISTRADOR

    def cambiar_rol(self, nuevo_rol: Rol) -> None:
        self.rol = nuevo_rol

    def cambiar_password(self, nuevo_hash: PasswordHash) -> None:
        self.password_hash = nuevo_hash

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def verificar_activo(self) -> None:
        """Lanza excepción si el usuario está inactivo"""
        if not self.activo:
            from core.domain.usuario.exceptions import UsuarioInactivoException
            raise UsuarioInactivoException(str(self.id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Usuario):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, email='{self.email.valor}', rol={self.rol.value})"