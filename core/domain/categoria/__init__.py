"""Módulo Categoria - Domain"""

from core.domain.categoria.categoria import Categoria
from core.domain.categoria.value_objects import CategoriaId, NombreCategoria
from core.domain.categoria.exceptions import (
    CategoriaIdInvalidoException,
    NombreCategoriaInvalidoException,
    CategoriaNoEncontradaException,
    CategoriaDuplicadaException,
)
from core.domain.categoria.repository import CategoriaRepository

__all__ = [
    'Categoria',
    'CategoriaId',
    'NombreCategoria',
    'CategoriaIdInvalidoException',
    'NombreCategoriaInvalidoException',
    'CategoriaNoEncontradaException',
    'CategoriaDuplicadaException',
    'CategoriaRepository',
]