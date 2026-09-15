# core/domain/producto/value_objects.py
"""Value Objects del dominio Producto"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import (
    ProductoIdInvalidoException,
    NombreProductoInvalidoException,
    PrecioInvalidoException,
    StockMinimoInvalidoException,
)
from core.i18n.message import MessageKey
from core.domain.shared.fecha import Fecha


# ============================================
# 1. ProductoId
# ============================================

@dataclass(frozen=True)
class ProductoId:
    """Value Object que identifica unívocamente a un Producto (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            try:
                object.__setattr__(self, "valor", UUID(self.valor))
            except (ValueError, AttributeError):
                raise ProductoIdInvalidoException(str(self.valor))

    @classmethod
    def generar(cls) -> ProductoId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> ProductoId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"ProductoId({self.valor})"


# ============================================
# 2. NombreProducto
# ============================================

@dataclass(frozen=True)
class NombreProducto:
    """Value Object que representa el nombre de un producto"""

    valor: str

    MIN_LENGTH: int = 3
    MAX_LENGTH: int = 50
    NOMBRES_RESERVADOS: tuple = ("admin", "root", "system", "test")

    def __post_init__(self):
        valor = self.valor
        min_len = self.MIN_LENGTH
        max_len = self.MAX_LENGTH

        if not valor or valor.strip() == "":
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_EMPTY, min=min_len, max=max_len
            )
        if len(valor) < min_len:
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_TOO_SHORT, min=min_len, max=max_len
            )
        if len(valor) > max_len:
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_TOO_LONG, min=min_len, max=max_len
            )
        if not valor.replace(" ", "").isalnum():
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_SPECIAL_CHARS, min=min_len, max=max_len
            )
        if valor.lower() in self.NOMBRES_RESERVADOS:
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_RESERVED, min=min_len, max=max_len
            )
        if valor[0].isdigit():
            raise NombreProductoInvalidoException(
                nombre=valor, razon=MessageKey.NAME_STARTS_WITH_NUMBER, min=min_len, max=max_len
            )


# ============================================
# 3. Precio
# ============================================

@dataclass(frozen=True)
class Precio:
    """Value Object que representa el precio de un producto"""
    valor: float

    def __post_init__(self):
        if self.valor <= 0:
            raise PrecioInvalidoException(self.valor)


# ============================================
# 4. Cantidad (ahora en core.domain.shared.cantidad)
# ============================================

# Cantidad vive en core/domain/shared/cantidad.py
# Se importa desde alli para compartirlo con MovimientoStock
from core.domain.shared.cantidad import Cantidad  # noqa: E402, F401

# ============================================
# 5. StockMinimo
# ============================================

@dataclass(frozen=True)
class StockMinimo:
    """Stock minimo permitido para un producto"""
    valor: int

    def __post_init__(self):
        if self.valor < 0:
            raise StockMinimoInvalidoException(self.valor)