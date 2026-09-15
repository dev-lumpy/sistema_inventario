"""Entidad Categoria (Aggregate Root)"""

from __future__ import annotations

from core.domain.categoria.value_objects import CategoriaId, NombreCategoria
from core.domain.shared.fecha import Fecha


class Categoria:
    """Entidad raíz del agregado Categoria"""

    def __init__(
        self,
        id: CategoriaId,
        nombre: NombreCategoria,
        activa: bool = True,
        fecha_creacion: Fecha | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.activa = activa
        self.fecha_creacion = fecha_creacion or Fecha.ahora()

    def renombrar(self, nuevo_nombre: NombreCategoria) -> None:
        self.nombre = nuevo_nombre

    def activar(self) -> None:
        self.activa = True

    def desactivar(self) -> None:
        self.activa = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Categoria):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Categoria(id={self.id}, nombre='{self.nombre.valor}', activa={self.activa})"