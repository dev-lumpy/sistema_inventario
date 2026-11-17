from __future__ import annotations

from core.domain.shared.errors import BusinessRuleViolation


class CompraNoEditableError(BusinessRuleViolation):
    code = "COMPRA_NO_EDITABLE"

    def __init__(self, estado: str) -> None:
        super().__init__(
            "Solo se puede modificar una compra en borrador", estado=estado
        )


class CompraSinLineasError(BusinessRuleViolation):
    code = "COMPRA_SIN_LINEAS"

    def __init__(self) -> None:
        super().__init__("No se puede confirmar una compra sin líneas")


class TransicionCompraInvalidaError(BusinessRuleViolation):
    code = "TRANSICION_COMPRA_INVALIDA"

    def __init__(self, estado_actual: str, accion: str) -> None:
        super().__init__(
            f"No se puede {accion} una compra en estado {estado_actual}",
            estado_actual=estado_actual,
            accion=accion,
        )


class ProveedorDeOtroAdministradorError(BusinessRuleViolation):
    code = "PROVEEDOR_DE_OTRO_ADMINISTRADOR"

    def __init__(self, proveedor_id: int, administrador_id: int) -> None:
        super().__init__(
            "El proveedor no pertenece al administrador",
            proveedor_id=proveedor_id,
            administrador_id=administrador_id,
        )


class LineaDeCompraDeOtroAdministradorError(BusinessRuleViolation):
    code = "LINEA_DE_COMPRA_DE_OTRO_ADMINISTRADOR"

    def __init__(self, administrador_id: int) -> None:
        super().__init__(
            "La línea de compra pertenece a otro administrador",
            administrador_id=administrador_id,
        )
