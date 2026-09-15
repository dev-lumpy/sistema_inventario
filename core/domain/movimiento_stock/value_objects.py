# core/domain/movimiento_stock/value_objects.py
"""Value Objects del dominio MovimientoStock"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import MovimientoIdInvalidoException


@dataclass(frozen=True)
class MovimientoId:
    """Value Object que identifica unívocamente a un MovimientoStock (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            try:
                object.__setattr__(self, "valor", UUID(self.valor))
            except (ValueError, AttributeError):
                raise MovimientoIdInvalidoException(str(self.valor))

    @classmethod
    def generar(cls) -> MovimientoId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> MovimientoId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"MovimientoId({self.valor})"