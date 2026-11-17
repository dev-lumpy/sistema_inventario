from __future__ import annotations

from core.domain.shared.errors import BusinessRuleViolation


class VentaNoEditableError(BusinessRuleViolation):
    code = "VENTA_NO_EDITABLE"

    def __init__(self, estado: str) -> None:
        super().__init__(
            "Solo se puede modificar una venta en borrador", estado=estado
        )


class VentaSinLineasError(BusinessRuleViolation):
    code = "VENTA_SIN_LINEAS"

    def __init__(self) -> None:
        super().__init__("No se puede confirmar una venta sin líneas")


class TransicionVentaInvalidaError(BusinessRuleViolation):
    code = "TRANSICION_VENTA_INVALIDA"

    def __init__(self, estado_actual: str, accion: str) -> None:
        super().__init__(
            f"No se puede {accion} una venta en estado {estado_actual}",
            estado_actual=estado_actual,
            accion=accion,
        )


class VentaConfirmadaNoEliminableError(BusinessRuleViolation):
    code = "VENTA_CONFIRMADA_NO_ELIMINABLE"

    def __init__(self, venta_id: int | None) -> None:
        super().__init__(
            "No se puede eliminar una venta confirmada; debe anularse",
            venta_id=venta_id,
        )


class LineaDeOtroAdministradorError(BusinessRuleViolation):
    code = "LINEA_DE_OTRO_ADMINISTRADOR"

    def __init__(self, administrador_id: int) -> None:
        super().__init__(
            "La línea pertenece a otro administrador",
            administrador_id=administrador_id,
        )
