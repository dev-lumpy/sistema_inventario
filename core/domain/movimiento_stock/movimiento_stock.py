"""Entidad MovimientoStock (Aggregate Root)"""

from __future__ import annotations

from core.domain.movimiento_stock.value_objects import MovimientoId
from core.domain.movimiento_stock.tipo_movimiento import TipoMovimiento
from core.domain.movimiento_stock.canal_venta import CanalVenta
from core.domain.movimiento_stock.exceptions import (
    ProveedorRequeridoParaEntradaException,
    CanalRequeridoParaSalidaException,
)
from core.domain.shared.cantidad import Cantidad
from core.domain.shared.fecha import Fecha
from core.domain.producto.value_objects import ProductoId
from core.domain.proveedor.value_objects import ProveedorId


class MovimientoStock:
    """Entidad raíz del agregado MovimientoStock"""

    def __init__(
        self,
        id: MovimientoId,
        producto_id: ProductoId,
        tipo: TipoMovimiento,
        cantidad: Cantidad,
        fecha: Fecha | None = None,
        proveedor_id: ProveedorId | None = None,
        canal_venta: CanalVenta | None = None,
    ):
        # Validaciones de invariantes
        if tipo == TipoMovimiento.ENTRADA and proveedor_id is None:
            raise ProveedorRequeridoParaEntradaException()
        if tipo == TipoMovimiento.ENTRADA and canal_venta is not None:
            raise ValueError("Una entrada no puede tener canal de venta")
        if tipo == TipoMovimiento.SALIDA and canal_venta is None:
            raise CanalRequeridoParaSalidaException()
        if tipo == TipoMovimiento.SALIDA and proveedor_id is not None:
            raise ValueError("Una salida no puede tener proveedor")
        if not cantidad.es_positivo():
            raise ValueError("La cantidad debe ser mayor a cero")

        self.id = id
        self.producto_id = producto_id
        self.tipo = tipo
        self.cantidad = cantidad
        self.fecha = fecha or Fecha.ahora()
        self.proveedor_id = proveedor_id
        self.canal_venta = canal_venta

    @classmethod
    def entrada(
        cls,
        producto_id: ProductoId,
        cantidad: Cantidad,
        proveedor_id: ProveedorId,
        fecha: Fecha | None = None,
    ) -> MovimientoStock:
        return cls(
            id=MovimientoId.generar(),
            producto_id=producto_id,
            tipo=TipoMovimiento.ENTRADA,
            cantidad=cantidad,
            fecha=fecha,
            proveedor_id=proveedor_id,
        )

    @classmethod
    def salida(
        cls,
        producto_id: ProductoId,
        cantidad: Cantidad,
        canal_venta: CanalVenta,
        fecha: Fecha | None = None,
    ) -> MovimientoStock:
        return cls(
            id=MovimientoId.generar(),
            producto_id=producto_id,
            tipo=TipoMovimiento.SALIDA,
            cantidad=cantidad,
            fecha=fecha,
            canal_venta=canal_venta,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MovimientoStock):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"MovimientoStock(id={self.id}, tipo={self.tipo.value}, "
            f"producto={self.producto_id}, cantidad={self.cantidad.valor})"
        )