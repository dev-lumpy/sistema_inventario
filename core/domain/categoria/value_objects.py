# core/domain/categoria/value_objects.py
"""Value Objects del dominio Categoria"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import (
    CategoriaIdInvalidoException,
    NombreCategoriaInvalidoException,
)


@dataclass(frozen=True)
class CategoriaId:
    """Value Object que identifica unívocamente a una Categoria (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            try:
                object.__setattr__(self, "valor", UUID(self.valor))
            except (ValueError, AttributeError):
                raise CategoriaIdInvalidoException(str(self.valor))

    @classmethod
    def generar(cls) -> CategoriaId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> CategoriaId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"CategoriaId({self.valor})"


@dataclass(frozen=True)
class NombreCategoria:
    """Value Object que representa el nombre de una categoría"""

    valor: str

    MIN_LENGTH: int = 2
    MAX_LENGTH: int = 50

    def __post_init__(self):
        valor = self.valor
        if not valor or valor.strip() == "":
            raise NombreCategoriaInvalidoException(
                nombre=valor,
                razon="CATEGORIA_NOMBRE_VACIO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )
        if len(valor.strip()) < self.MIN_LENGTH:
            raise NombreCategoriaInvalidoException(
                nombre=valor,
                razon="CATEGORIA_NOMBRE_CORTO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )
        if len(valor) > self.MAX_LENGTH:
            raise NombreCategoriaInvalidoException(
                nombre=valor,
                razon="CATEGORIA_NOMBRE_LARGO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )