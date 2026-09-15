"""Caso de uso: RegistrarEntradaStock (RF-02)"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.producto.repository import ProductoRepository
from core.domain.producto.value_objects import ProductoId, Cantidad
from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.repository import MovimientoStockRepository
from core.domain.proveedor.value_objects import ProveedorId
from core.domain.proveedor.repository import ProveedorRepository
from core.domain.producto.exceptions import ProductoNoEncontradoException


@dataclass
class RegistrarEntradaStockInput:
    producto_id: str
    cantidad: int
    proveedor_id: str


@dataclass
class RegistrarEntradaStockOutput:
    movimiento_id: str


class RegistrarEntradaStock:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        proveedor_repo: ProveedorRepository,
        movimiento_repo: MovimientoStockRepository,
    ):
        self._producto_repo = producto_repo
        self._proveedor_repo = proveedor_repo
        self._movimiento_repo = movimiento_repo

    def ejecutar(self, input: RegistrarEntradaStockInput) -> RegistrarEntradaStockOutput:
        producto_id = ProductoId.desde_str(input.producto_id)
        producto = self._producto_repo.obtener_por_id(producto_id)
        if producto is None:
            raise ProductoNoEncontradoException(input.producto_id)

        proveedor_id = ProveedorId.desde_str(input.proveedor_id)
        proveedor = self._proveedor_repo.obtener_por_id(proveedor_id)
        if proveedor is None:
            raise ProveedorNoEncontradoException(input.proveedor_id)

        producto.aumentar_stock(input.cantidad)
        movimiento = MovimientoStock.entrada(
            producto_id=producto_id,
            cantidad=Cantidad(input.cantidad),
            proveedor_id=proveedor_id,
        )

        self._producto_repo.guardar(producto)
        self._movimiento_repo.guardar(movimiento)

        return RegistrarEntradaStockOutput(movimiento_id=str(movimiento.id))