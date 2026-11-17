from __future__ import annotations

import re
from dataclasses import dataclass

from core.domain.shared.errors import ValidationError
from core.domain.shared.validators import texto_opcional, texto_requerido

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_CORREO_RE = re.compile(
    r"^(?=.{1,254}$)"
    r"[A-Za-z0-9._%+-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}$"
)


@dataclass(frozen=True)
class Nombre:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_requerido(self.valor, "nombre", 100))


@dataclass(frozen=True)
class Apellidos:
    valor: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_opcional(self.valor, "apellidos", 100))


@dataclass(frozen=True)
class UserName:
    valor: str

    def __post_init__(self) -> None:
        limpio = texto_requerido(self.valor, "user_name", 50)
        if len(limpio) < 3:
            raise ValidationError("El user_name debe tener al menos 3 caracteres")
        if not _USERNAME_RE.match(limpio):
            raise ValidationError(
                "El user_name solo admite letras, números, punto, guion y guion bajo"
            )
        object.__setattr__(self, "valor", limpio)


@dataclass(frozen=True)
class Correo:
    valor: str

    def __post_init__(self) -> None:
        limpio = texto_requerido(self.valor, "correo", 150).lower()
        if not _CORREO_RE.match(limpio):
            raise ValidationError("El correo no tiene un formato válido", correo=limpio)
        object.__setattr__(self, "valor", limpio)


@dataclass(frozen=True)
class PasswordHash:
    valor: str

    def __post_init__(self) -> None:
        if not self.valor or not str(self.valor).strip():
            raise ValidationError("El hash de contraseña no puede estar vacío")
        object.__setattr__(self, "valor", str(self.valor).strip())


@dataclass(frozen=True)
class NombreNegocio:
    valor: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "valor", texto_opcional(self.valor, "nombre_negocio", 150)
        )


@dataclass(frozen=True)
class Moneda:
    valor: str = "BOB"

    def __post_init__(self) -> None:
        limpio = str(self.valor or "BOB").strip().upper()
        if len(limpio) != 3 or not limpio.isalpha():
            raise ValidationError("La moneda debe ser un código de 3 letras")
        object.__setattr__(self, "valor", limpio)
