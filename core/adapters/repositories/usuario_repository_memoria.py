"""Repositorio en memoria para Usuario (tests y desarrollo)"""

from __future__ import annotations

from typing import Optional
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.value_objects import UsuarioId, Email


class UsuarioRepositoryMemoria(UsuarioRepository):
    def __init__(self):
        self._usuarios: dict[str, Usuario] = {}

    def guardar(self, usuario: Usuario) -> None:
        self._usuarios[str(usuario.id)] = usuario

    def obtener_por_id(self, id: UsuarioId) -> Optional[Usuario]:
        return self._usuarios.get(str(id))

    def obtener_por_email(self, email: Email) -> Optional[Usuario]:
        for u in self._usuarios.values():
            if u.email.valor == email.valor:
                return u
        return None

    def listar_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def eliminar(self, id: UsuarioId) -> None:
        self._usuarios.pop(str(id), None)