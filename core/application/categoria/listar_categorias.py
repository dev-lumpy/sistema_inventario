"""Caso de uso: ListarCategorias (RF-12)"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.domain.categoria.categoria import Categoria
from core.domain.categoria.repository import CategoriaRepository


@dataclass
class ListarCategoriasOutput:
    categorias: list[Categoria] = field(default_factory=list)


class ListarCategorias:
    def __init__(self, categoria_repo: CategoriaRepository):
        self._categoria_repo = categoria_repo

    def ejecutar(self) -> ListarCategoriasOutput:
        categorias = self._categoria_repo.listar_todas()
        return ListarCategoriasOutput(categorias=categorias)