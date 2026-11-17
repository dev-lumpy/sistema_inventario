from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from core.domain.catalog.entities import MovimientoInventario
from core.domain.catalog.exceptions import StockInsuficienteError
from core.domain.shared.value_objects import Quantity


def calcular_stock(movimientos: Iterable[MovimientoInventario]) -> Decimal:
    total = Decimal("0")
    for movimiento in movimientos:
        total += movimiento.motivo.signo * movimiento.cantidad.value
    return total


def verificar_stock_suficiente(
    producto_id: int,
    stock_disponible: Decimal,
    cantidad_solicitada: Quantity,
) -> None:
    if stock_disponible < cantidad_solicitada.value:
        raise StockInsuficienteError(
            producto_id=producto_id,
            disponible=str(stock_disponible),
            solicitado=str(cantidad_solicitada.value),
        )
