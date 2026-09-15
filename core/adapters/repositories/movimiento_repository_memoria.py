"""Repositorio en memoria para MovimientoStock (tests y desarrollo)"""

from __future__ import annotations

from typing import Optional
from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.repository import MovimientoStockRepository
from core.domain.movimiento_stock.value_objects import MovimientoId
from core.domain.movimiento_stock.tipo_movimiento import TipoMovimiento
from core.domain.producto.value_objects import ProductoId
from core.domain.shared.fecha import Fecha


class MovimientoStockRepositoryMemoria(MovimientoStockRepository):
    def __init__(self):
        self._movimientos: list[MovimientoStock] = []

    def guardar(self, movimiento: MovimientoStock) -> None:
        self._movimientos.append(movimiento)

    def obtener_por_id(self, id: MovimientoId) -> Optional[MovimientoStock]:
        for m in self._movimientos:
            if m.id == id:
                return m
        return None

    def listar_por_producto(self, producto_id: ProductoId) -> list[MovimientoStock]:
        return sorted(
            [m for m in self._movimientos if m.producto_id == producto_id],
            key=lambda m: m.fecha.valor,
            reverse=True,
        )

    def listar_por_periodo(self, desde: Fecha, hasta: Fecha) -> list[MovimientoStock]:
        return [
            m
            for m in self._movimientos
            if not m.fecha.es_antes_de(desde) and not m.fecha.es_despues_de(hasta)
        ]

    def productos_mas_vendidos(
        self, desde: Fecha, hasta: Fecha, limite: int = 10
    ) -> list[tuple[ProductoId, int]]:
        ventas: dict[str, int] = {}
        for m in self._movimientos:
            if m.tipo == TipoMovimiento.SALIDA:
                key = str(m.producto_id)
                ventas[key] = ventas.get(key, 0) + m.cantidad.valor
        sorted_ventas = sorted(ventas.items(), key=lambda x: x[1], reverse=True)
        return [
            (ProductoId.desde_str(pid), cant)
            for pid, cant in sorted_ventas[:limite]
        ]