"""Caso de uso: CrearCategoria (RF-12)"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.categoria.categoria import Categoria
from core.domain.categoria.repository import CategoriaRepository
from core.domain.categoria.value_objects import CategoriaId, NombreCategoria


@dataclass
class CrearCategoriaInput:
    nombre: str


@dataclass
class CrearCategoriaOutput:
    categoria_id: str


class CrearCategoria:
    def __init__(self, categoria_repo: CategoriaRepository):
        self._categoria_repo = categoria_repo

    def ejecutar(self, input: CrearCategoriaInput) -> CrearCategoriaOutput:
        categoria = Categoria(
            id=CategoriaId.generar(),
            nombre=NombreCategoria(input.nombre),
        )
        self._categoria_repo.guardar(categoria)
        return CrearCategoriaOutput(categoria_id=str(categoria.id))