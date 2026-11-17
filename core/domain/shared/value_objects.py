from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

from core.domain.shared.errors import ValidationError

CENTAVO = Decimal("0.01")
MILESIMA = Decimal("0.001")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BOB"

    def __post_init__(self) -> None:
        try:
            amount = Decimal(str(self.amount)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
        except Exception as exc:
            raise ValidationError("Monto inválido", amount=str(self.amount)) from exc
        if amount < 0:
            raise ValidationError("El monto no puede ser negativo", amount=str(amount))
        currency = str(self.currency).strip().upper()
        if len(currency) != 3:
            raise ValidationError("La moneda debe tener 3 letras", currency=self.currency)
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", currency)

    @classmethod
    def cero(cls, currency: str = "BOB") -> Money:
        return cls(Decimal("0"), currency)

    @classmethod
    def desde(cls, valor: Union[int, float, str, Decimal], currency: str = "BOB") -> Money:
        return cls(Decimal(str(valor)), currency)

    def _misma_moneda(self, otra: Money) -> None:
        if self.currency != otra.currency:
            raise ValidationError(
                "No se pueden operar montos de distinta moneda",
                moneda_a=self.currency,
                moneda_b=otra.currency,
            )

    def __add__(self, otra: Money) -> Money:
        self._misma_moneda(otra)
        return Money(self.amount + otra.amount, self.currency)

    def __sub__(self, otra: Money) -> Money:
        self._misma_moneda(otra)
        resultado = self.amount - otra.amount
        if resultado < 0:
            raise ValidationError("El resultado del monto no puede ser negativo")
        return Money(resultado, self.currency)

    def __mul__(self, factor: Union[int, float, Decimal, Quantity]) -> Money:
        valor = factor.value if isinstance(factor, Quantity) else Decimal(str(factor))
        if valor < 0:
            raise ValidationError("El factor no puede ser negativo")
        return Money(self.amount * valor, self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> Money:
        valor = Decimal(str(divisor))
        if valor <= 0:
            raise ValidationError("El divisor debe ser mayor que cero")
        return Money(self.amount / valor, self.currency)

    def es_cero(self) -> bool:
        return self.amount == 0

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class Quantity:
    value: Decimal

    def __post_init__(self) -> None:
        try:
            value = Decimal(str(self.value)).quantize(MILESIMA, rounding=ROUND_HALF_UP)
        except Exception as exc:
            raise ValidationError("Cantidad inválida", value=str(self.value)) from exc
        if value <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero", value=str(value))
        object.__setattr__(self, "value", value)

    @classmethod
    def desde(cls, valor: Union[int, float, str, Decimal]) -> Quantity:
        return cls(Decimal(str(valor)))

    def __add__(self, otra: Quantity) -> Quantity:
        return Quantity(self.value + otra.value)

    def __sub__(self, otra: Quantity) -> Quantity:
        resultado = self.value - otra.value
        if resultado < 0:
            raise ValidationError("La cantidad resultante no puede ser negativa")
        return Quantity(resultado)

    def es_mayor_que(self, otra: Quantity) -> bool:
        return self.value > otra.value

    def __str__(self) -> str:
        return f"{self.value.normalize():f}"
