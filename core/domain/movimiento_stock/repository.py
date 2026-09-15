"""Interfaz del repositorio de MovimientoStock (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.value_objects import MovimientoId
from core.domain.producto.value_objects import ProductoId
from core.domain.shared.fecha import Fecha


class MovimientoStockRepository(ABC):
    @abstractmethod
    def guardar(self, movimiento: MovimientoStock) -> None:
        ...

    @abstractmethod
    def obtener_por_id(self, id: MovimientoId) -> Optional[MovimientoStock]:
        ...

    @abstractmethod
    def listar_por_producto(
        self, producto_id: ProductoId
    ) -> list[MovimientoStock]:
        """Ordenado: reciente -> antiguo"""
        ...

    @abstractmethod
    def listar_por_periodo(
        self, desde: Fecha, hasta: Fecha
    ) -> list[MovimientoStock]:
        ...

    @abstractmethod
    def productos_mas_vendidos(
        self, desde: Fecha, hasta: Fecha, limite: int = 10
    ) -> list[tuple[ProductoId, int]]:
        """Retorna [(ProductoId, cantidad_vendida), ...] ordenado descendente"""
        ...