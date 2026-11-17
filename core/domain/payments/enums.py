from __future__ import annotations

from enum import Enum


class MetodoPago(str, Enum):
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    QR = "qr"
    TARJETA = "tarjeta"
    OTRO = "otro"
