"""Repositorio en memoria para Categoria (tests y desarrollo)"""

from __future__ import annotations

from typing import Optional
from core.domain.categoria.categoria import Categoria
from core.domain.categoria.repository import CategoriaRepository
from core.domain.categoria.value_objects import CategoriaId, NombreCategoria


class CategoriaRepositoryMemoria(CategoriaRepository):
    def __init__(self):
        self._categorias: dict[str, Categoria] = {}

    def guardar(self, categoria: Categoria) -> None:
        self._categorias[str(categoria.id)] = categoria

    def obtener_por_id(self, id: CategoriaId) -> Optional[Categoria]:
        return self._categorias.get(str(id))

    def obtener_por_nombre(self, nombre: NombreCategoria) -> Optional[Categoria]:
        for c in self._categorias.values():
            if c.nombre.valor == nombre.valor:
                return c
        return None

    def listar_todas(self) -> list[Categoria]:
        return list(self._categorias.values())

    def eliminar(self, id: CategoriaId) -> None:
        self._categorias.pop(str(id), None)