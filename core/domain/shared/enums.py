from __future__ import annotations

from enum import Enum


class TipoCliente(str, Enum):
    INDIVIDUAL = "individual"
    PRODUCTOR = "productor"
    MAYOREO = "mayoreo"

    @classmethod
    def desde(cls, valor: str) -> TipoCliente:
        try:
            return cls(valor)
        except ValueError as exc:
            from core.domain.shared.errors import ValidationError

            raise ValidationError(f"Tipo de cliente inválido: {valor}") from exc
