# core/domain/movimiento_stock/exceptions.py
"""Excepciones del dominio MovimientoStock"""

from core.domain.shared.exceptions import DomainException


class MovimientoIdInvalidoException(DomainException):
    def __init__(self, id: str):
        super().__init__(
            code="MOVIMIENTO_ID_INVALIDO",
            message=f"ID de movimiento inválido: {id}",
            status_code=400,
            field="ID de movimiento",
            id=id,
        )


class MovimientoNoEncontradoException(DomainException):
    def __init__(self, movimiento_id: str):
        super().__init__(
            code="MOVIMIENTO_NO_ENCONTRADO",
            message=f"Movimiento no encontrado: {movimiento_id}",
            status_code=404,
            movimiento_id=movimiento_id,
        )


class ProveedorRequeridoParaEntradaException(DomainException):
    """Una entrada de stock debe tener un proveedor"""

    def __init__(self):
        super().__init__(
            code="ENTRADA_REQUIERE_PROVEEDOR",
            message="Una entrada de stock debe tener un proveedor asociado",
            status_code=400,
        )


class CanalRequeridoParaSalidaException(DomainException):
    """Una salida de stock debe tener un canal de venta"""

    def __init__(self):
        super().__init__(
            code="SALIDA_REQUIERE_CANAL",
            message="Una salida de stock debe tener un canal de venta asociado",
            status_code=400,
        )