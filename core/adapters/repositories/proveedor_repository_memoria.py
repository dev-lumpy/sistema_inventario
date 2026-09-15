"""Repositorio en memoria para Proveedor (tests y desarrollo)"""

from __future__ import annotations

from typing import Optional
from core.domain.proveedor.proveedor import Proveedor
from core.domain.proveedor.repository import ProveedorRepository
from core.domain.proveedor.value_objects import ProveedorId


class ProveedorRepositoryMemoria(ProveedorRepository):
    def __init__(self):
        self._proveedores: dict[str, Proveedor] = {}

    def guardar(self, proveedor: Proveedor) -> None:
        self._proveedores[str(proveedor.id)] = proveedor

    def obtener_por_id(self, id: ProveedorId) -> Optional[Proveedor]:
        return self._proveedores.get(str(id))

    def listar_todos(self) -> list[Proveedor]:
        return list(self._proveedores.values())

    def eliminar(self, id: ProveedorId) -> None:
        self._proveedores.pop(str(id), None)