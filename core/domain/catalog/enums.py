from __future__ import annotations

from enum import Enum


class MotivoMovimiento(str, Enum):
    COMPRA = "compra"
    VENTA = "venta"
    DEVOLUCION = "devolucion"
    MERMA = "merma"
    AJUSTE_POS = "ajuste_pos"
    AJUSTE_NEG = "ajuste_neg"

    @property
    def es_entrada(self) -> bool:
        return self in (
            MotivoMovimiento.COMPRA,
            MotivoMovimiento.DEVOLUCION,
            MotivoMovimiento.AJUSTE_POS,
        )

    @property
    def es_salida(self) -> bool:
        return not self.es_entrada

    @property
    def signo(self) -> int:
        return 1 if self.es_entrada else -1


class ReferenciaTipo(str, Enum):
    VENTA = "venta"
    COMPRA = "compra"
    AJUSTE = "ajuste"
