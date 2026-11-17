from __future__ import annotations

from enum import Enum


class EstadoCompra(str, Enum):
    BORRADOR = "borrador"
    CONFIRMADA = "confirmada"
    ANULADA = "anulada"
