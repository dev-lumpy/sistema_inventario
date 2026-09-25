"""Entidad Usuario (Aggregate Root)"""

from __future__ import annotations
from typing import Optional
from enum import Enum

from core.domain.usuario.value_objects import (
    RolUser,
    UsuarioId,
    Email,
    NombreUsuario,
    PasswordHash,
    EstadoUsuario
)
from core.domain.usuario.rol import Rol
from core.domain.usuario.exceptions import (
    UsuarioInactivoException
)
from core.domain.shared.fecha import Fecha


class Usuario:
    """Entidad raíz del agregado Usuario.

    Representa tanto a administradores como a vendedores.
    La relación admin→vendedor NO vive aquí; vive en el repositorio.
    """

    def __init__(
        self,
        id: UsuarioId,
        nombre: NombreUsuario,
        email: Email,
        password_hash: PasswordHash,
        rol: RolUser,
        activo: EstadoUsuario,
        fecha_creacion: Fecha | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo
        self.fecha_creacion = fecha_creacion or Fecha.ahora()

    def es_vendedor(self) -> bool:
        return self.rol.es_vendedor

    def es_administrador(self) -> bool:
        return self.rol.es_administrador

    def puede_configurar(self) -> bool:
        return self.rol.es_administrador

    def activar(self) -> None:
        self.activo = EstadoUsuario.activo()

    def desactivar(self) -> None:
        self.activo = EstadoUsuario.activo()

    def verificar_activo(self) -> None:
        if self.activo.valor != EstadoUsuario.ACTIVO:
            raise UsuarioInactivoException(str(self.id))

    def cambiar_password(self, nuevo_hash: PasswordHash) -> None:
        self.password_hash = nuevo_hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Usuario):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, email='{self.email.valor}', "
            f"rol={self.rol.valor}, activo={self.activo.valor})"
        )

