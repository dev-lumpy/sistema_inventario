"""Caso de uso: ObtenerProductosEnAlerta (RF-05, HU-04)"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.domain.producto.producto import Producto
from core.domain.producto.repository import ProductoRepository


@dataclass
class ObtenerProductosEnAlertaOutput:
    productos: list[Producto] = field(default_factory=list)


class ObtenerProductosEnAlerta:
    """Obtiene productos cuyo stock está por debajo del mínimo"""

    def __init__(self, producto_repo: ProductoRepository):
        self._producto_repo = producto_repo

    def ejecutar(self) -> ObtenerProductosEnAlertaOutput:
        productos = self._producto_repo.listar_en_alerta()
        return ObtenerProductosEnAlertaOutput(productos=productos)