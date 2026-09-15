"""Caso de uso: ObtenerHistorialMovimientos (RF-08, HU-05)"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.repository import MovimientoStockRepository
from core.domain.producto.value_objects import ProductoId
from core.domain.producto.exceptions import ProductoNoEncontradoException
from core.domain.producto.repository import ProductoRepository


@dataclass
class ObtenerHistorialMovimientosInput:
    producto_id: str


@dataclass
class ObtenerHistorialMovimientosOutput:
    movimientos: list[MovimientoStock] = field(default_factory=list)


class ObtenerHistorialMovimientos:
    def __init__(
        self,
        movimiento_repo: MovimientoStockRepository,
        producto_repo: ProductoRepository,
    ):
        self._movimiento_repo = movimiento_repo
        self._producto_repo = producto_repo

    def ejecutar(
        self, input: ObtenerHistorialMovimientosInput
    ) -> ObtenerHistorialMovimientosOutput:
        producto_id = ProductoId.desde_str(input.producto_id)
        producto = self._producto_repo.obtener_por_id(producto_id)
        if producto is None:
            raise ProductoNoEncontradoException(input.producto_id)

        movimientos = self._movimiento_repo.listar_por_producto(producto_id)
        return ObtenerHistorialMovimientosOutput(movimientos=movimientos)