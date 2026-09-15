"""Interfaz del repositorio de Proveedor (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.proveedor.proveedor import Proveedor
from core.domain.proveedor.value_objects import ProveedorId


class ProveedorRepository(ABC):
    @abstractmethod
    def guardar(self, proveedor: Proveedor) -> None:
        ...

    @abstractmethod
    def obtener_por_id(self, id: ProveedorId) -> Optional[Proveedor]:
        ...

    @abstractmethod
    def listar_todos(self) -> list[Proveedor]:
        ...

    @abstractmethod
    def eliminar(self, id: ProveedorId) -> None:
        ...