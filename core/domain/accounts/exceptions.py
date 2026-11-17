from __future__ import annotations

from core.domain.shared.errors import BusinessRuleViolation, PermissionDeniedError


class UsuarioInactivoError(PermissionDeniedError):
    code = "USUARIO_INACTIVO"

    def __init__(self, usuario_id: int | None) -> None:
        super().__init__("El usuario está inactivo", usuario_id=usuario_id)


class VinculoNoAceptadoError(BusinessRuleViolation):
    code = "VINCULO_NO_ACEPTADO"

    def __init__(self, vendedor_id: int, administrador_id: int, estado: str) -> None:
        super().__init__(
            "El vínculo vendedor/administrador no está aceptado",
            vendedor_id=vendedor_id,
            administrador_id=administrador_id,
            estado=estado,
        )


class VendedorBloqueadoError(BusinessRuleViolation):
    code = "VENDEDOR_BLOQUEADO"

    def __init__(self, vendedor_id: int) -> None:
        super().__init__("El vendedor está bloqueado", vendedor_id=vendedor_id)


class TransicionVinculoInvalidaError(BusinessRuleViolation):
    code = "TRANSICION_VINCULO_INVALIDA"

    def __init__(self, estado_actual: str, accion: str) -> None:
        super().__init__(
            f"No se puede {accion} un vínculo en estado {estado_actual}",
            estado_actual=estado_actual,
            accion=accion,
        )
