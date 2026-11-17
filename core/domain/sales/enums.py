from __future__ import annotations

from enum import Enum


class EstadoVenta(str, Enum):
    BORRADOR = "borrador"
    CONFIRMADA = "confirmada"
    ANULADA = "anulada"


class CanalVenta(str, Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    PRESENCIAL = "presencial"
    OTRO = "otro"

    @classmethod
    def desde(cls, valor: str) -> CanalVenta:
        try:
            return cls(valor)
        except ValueError as exc:
            from core.domain.shared.errors import ValidationError

            raise ValidationError(f"Canal de venta inválido: {valor}") from exc
