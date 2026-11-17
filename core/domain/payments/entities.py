from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.domain.payments.enums import MetodoPago
from core.domain.shared.clock import now
from core.domain.shared.errors import ValidationError
from core.domain.shared.value_objects import Money


@dataclass
class Pago:
    administrador_id: int
    venta_id: int
    metodo: MetodoPago
    monto: Money
    id: int | None = None
    fecha: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if self.monto.amount <= 0:
            raise ValidationError("El monto del pago debe ser mayor que cero")

    def pertenece_a(self, administrador_id: int) -> bool:
        return self.administrador_id == administrador_id
