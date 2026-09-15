"""Caso de uso: AutenticarUsuario (RF-10)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.value_objects import Email
from core.domain.usuario.exceptions import (
    UsuarioNoEncontradoException,
    UsuarioInactivoException,
)
from core.application.ports.password_hasher import PasswordHasher


@dataclass
class AutenticarUsuarioInput:
    email: str
    password: str


@dataclass
class AutenticarUsuarioOutput:
    usuario_id: str
    nombre: str
    email: str
    rol: str


class AutenticarUsuario:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        password_hasher: PasswordHasher,
    ):
        self._usuario_repo = usuario_repo
        self._password_hasher = password_hasher

    def ejecutar(
        self, input: AutenticarUsuarioInput
    ) -> Optional[AutenticarUsuarioOutput]:
        email = Email(input.email)
        usuario = self._usuario_repo.obtener_por_email(email)
        if usuario is None:
            return None

        usuario.verificar_activo()

        if not self._password_hasher.verificar(input.password, usuario.password_hash.valor):
            return None

        return AutenticarUsuarioOutput(
            usuario_id=str(usuario.id),
            nombre=usuario.nombre.valor,
            email=usuario.email.valor,
            rol=usuario.rol.value,
        )