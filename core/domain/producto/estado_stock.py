"""Enum EstadoStock para Producto"""

from enum import Enum


class EstadoStock(Enum):
    DISPONIBLE = "disponible"
    BAJO = "bajo"
    AGOTADO = "agotado"

    @property
    def color(self) -> str:
        return {"disponible": "verde", "bajo": "amarillo", "agotado": "rojo"}[self.value]

    @property
    def requiere_accion(self) -> bool:
        return self in (EstadoStock.BAJO, EstadoStock.AGOTADO)