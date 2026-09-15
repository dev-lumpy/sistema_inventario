"""Interfaz del repositorio de Categoria (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.categoria.categoria import Categoria
from core.domain.categoria.value_objects import CategoriaId, NombreCategoria


class CategoriaRepository(ABC):
    """Puerto secundario: persistencia de Categorias"""

    @abstractmethod
    def guardar(self, categoria: Categoria) -> None:
        ...

    @abstractmethod
    def obtener_por_id(self, id: CategoriaId) -> Optional[Categoria]:
        ...

    @abstractmethod
    def obtener_por_nombre(self, nombre: NombreCategoria) -> Optional[Categoria]:
        ...

    @abstractmethod
    def listar_todas(self) -> list[Categoria]:
        ...

    @abstractmethod
    def eliminar(self, id: CategoriaId) -> None:
        ...