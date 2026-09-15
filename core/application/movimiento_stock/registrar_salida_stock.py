"""Caso de uso: RegistrarSalidaStock (RF-03, HU-02)"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.producto.repository import ProductoRepository
from core.domain.producto.value_objects import ProductoId, Cantidad
from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.repository import MovimientoStockRepository
from core.domain.movimiento_stock.canal_venta import CanalVenta
from core.domain.producto.exceptions import ProductoNoEncontradoException


@dataclass
class RegistrarSalidaStockInput:
    producto_id: str
    cantidad: int
    canal_venta: str


@dataclass
class RegistrarSalidaStockOutput:
    movimiento_id: str


class RegistrarSalidaStock:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        movimiento_repo: MovimientoStockRepository,
    ):
        self._producto_repo = producto_repo
        self._movimiento_repo = movimiento_repo

    def ejecutar(self, input: RegistrarSalidaStockInput) -> RegistrarSalidaStockOutput:
        producto_id = ProductoId.desde_str(input.producto_id)
        producto = self._producto_repo.obtener_por_id(producto_id)
        if producto is None:
            raise ProductoNoEncontradoException(input.producto_id)

        producto.reducir_stock(input.cantidad)
        movimiento = MovimientoStock.salida(
            producto_id=producto_id,
            cantidad=Cantidad(input.cantidad),
            canal_venta=CanalVenta(input.canal_venta),
        )

        self._producto_repo.guardar(producto)
        self._movimiento_repo.guardar(movimiento)

        return RegistrarSalidaStockOutput(movimiento_id=str(movimiento.id))