"""Interfaz del repositorio de Usuario (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import UsuarioId, Email


class UsuarioRepository(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> None:
        ...

    @abstractmethod
    def obtener_por_id(self, id: UsuarioId) -> Optional[Usuario]:
        ...

    @abstractmethod
    def obtener_por_email(self, email: Email) -> Optional[Usuario]:
        ...

    @abstractmethod
    def listar_todos(self) -> list[Usuario]:
        ...

    @abstractmethod
    def eliminar(self, id: UsuarioId) -> None:
        ...