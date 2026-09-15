"""Enum TipoMovimiento para MovimientoStock"""

from enum import Enum


class TipoMovimiento(Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"