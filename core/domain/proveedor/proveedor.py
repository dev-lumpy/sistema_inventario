"""Entidad Proveedor (Aggregate Root)"""

from __future__ import annotations

from core.domain.proveedor.value_objects import (
    ProveedorId,
    NombreProveedor,
    ContactoProveedor,
)
from core.domain.shared.fecha import Fecha


class Proveedor:
    """Entidad raíz del agregado Proveedor"""

    def __init__(
        self,
        id: ProveedorId,
        nombre: NombreProveedor,
        contacto: ContactoProveedor | None = None,
        activo: bool = True,
        fecha_creacion: Fecha | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.contacto = contacto or ContactoProveedor("")
        self.activo = activo
        self.fecha_creacion = fecha_creacion or Fecha.ahora()

    def actualizar_contacto(self, nuevo_contacto: ContactoProveedor) -> None:
        self.contacto = nuevo_contacto

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Proveedor):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Proveedor(id={self.id}, nombre='{self.nombre.valor}', activo={self.activo})"