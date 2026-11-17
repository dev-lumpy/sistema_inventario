from __future__ import annotations

from core.domain.shared.errors import BusinessRuleViolation, ValidationError


class CategoriaDeOtroAdministradorError(BusinessRuleViolation):
    code = "CATEGORIA_DE_OTRO_ADMINISTRADOR"

    def __init__(self, categoria_id: int, administrador_id: int) -> None:
        super().__init__(
            "La categoría no pertenece al administrador",
            categoria_id=categoria_id,
            administrador_id=administrador_id,
        )


class ProductoDeOtroAdministradorError(BusinessRuleViolation):
    code = "PRODUCTO_DE_OTRO_ADMINISTRADOR"

    def __init__(self, producto_id: int, administrador_id: int) -> None:
        super().__init__(
            "El producto no pertenece al administrador",
            producto_id=producto_id,
            administrador_id=administrador_id,
        )


class PrecioNoVigenteError(BusinessRuleViolation):
    code = "PRECIO_NO_VIGENTE"

    def __init__(self, producto_id: int, tipo_cliente: str) -> None:
        super().__init__(
            "No existe una tarifa vigente para el producto y tipo de cliente",
            producto_id=producto_id,
            tipo_cliente=tipo_cliente,
        )


class StockInsuficienteError(BusinessRuleViolation):
    code = "STOCK_INSUFICIENTE"

    def __init__(self, producto_id: int, disponible: str, solicitado: str) -> None:
        super().__init__(
            "Stock insuficiente para completar la operación",
            producto_id=producto_id,
            disponible=disponible,
            solicitado=solicitado,
        )


class VigenciaInvalidaError(ValidationError):
    code = "VIGENCIA_INVALIDA"

    def __init__(self) -> None:
        super().__init__("La fecha de fin de vigencia debe ser posterior al inicio")
