"""Interfaz del repositorio de Usuario (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import UsuarioId, Email


class UsuarioRepository(ABC):
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
    def obtener_administradores(self) -> list[Usuario]:
        ...

    @abstractmethod
    def eliminar(self, id: UsuarioId) -> None:
        ...

    @abstractmethod
    def guardar_administrador(self, usuario: Usuario) -> None:
        ...

    @abstractmethod
    def guardar_vendedor_con_admin(
            self, 
            vendedor: Usuario,
            admin_id: UsuarioId
    ) -> None:
        ...


