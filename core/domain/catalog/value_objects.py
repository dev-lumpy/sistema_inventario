from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.domain.shared.errors import ValidationError
from core.domain.shared.validators import texto_requerido


@dataclass(frozen=True)
class NombreCategoria:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_requerido(self.valor, "categoría", 100))


@dataclass(frozen=True)
class NombreProducto:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_requerido(self.valor, "producto", 200))


@dataclass(frozen=True)
class StockMinimo:
    valor: Decimal

    def __post_init__(self) -> None:
        try:
            valor = Decimal(str(self.valor)).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
        except Exception as exc:
            raise ValidationError("Stock mínimo inválido", valor=str(self.valor)) from exc
        if valor < 0:
            raise ValidationError("El stock mínimo no puede ser negativo")
        object.__setattr__(self, "valor", valor)

    @classmethod
    def cero(cls) -> StockMinimo:
        return cls(Decimal("0"))
