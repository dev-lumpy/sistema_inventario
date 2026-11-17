from __future__ import annotations

from core.domain.shared.errors import ValidationError


def texto_requerido(valor: str | None, campo: str, max_length: int) -> str:
    if valor is None or not str(valor).strip():
        raise ValidationError(f"El campo {campo} es obligatorio", campo=campo)
    limpio = str(valor).strip()
    if len(limpio) > max_length:
        raise ValidationError(
            f"El campo {campo} no puede superar {max_length} caracteres",
            campo=campo,
            max_length=max_length,
        )
    return limpio


def texto_opcional(valor: str | None, campo: str, max_length: int) -> str | None:
    if valor is None:
        return None
    limpio = str(valor).strip()
    if not limpio:
        return None
    if len(limpio) > max_length:
        raise ValidationError(
            f"El campo {campo} no puede superar {max_length} caracteres",
            campo=campo,
            max_length=max_length,
        )
    return limpio


def entero_positivo(valor: int | None, campo: str) -> int:
    if valor is None or int(valor) <= 0:
        raise ValidationError(f"El campo {campo} debe ser un entero positivo", campo=campo)
    return int(valor)
