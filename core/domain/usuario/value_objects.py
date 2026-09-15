# core/domain/usuario/value_objects.py
"""Value Objects del dominio Usuario"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import UsuarioIdInvalidoException, EmailInvalidoException


@dataclass(frozen=True)
class UsuarioId:
    """Value Object que identifica unívocamente a un Usuario (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            try:
                object.__setattr__(self, "valor", UUID(self.valor))
            except (ValueError, AttributeError):
                raise UsuarioIdInvalidoException(str(self.valor))

    @classmethod
    def generar(cls) -> UsuarioId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> UsuarioId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"UsuarioId({self.valor})"


@dataclass(frozen=True)
class Email:
    """Value Object que representa un email válido"""
    valor: str

    def __post_init__(self):
        valor = self.valor.strip().lower()
        object.__setattr__(self, "valor", valor)
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise EmailInvalidoException(valor)


@dataclass(frozen=True)
class NombreUsuario:
    """Value Object que representa el nombre de un usuario"""
    valor: str

    MIN_LENGTH: int = 2
    MAX_LENGTH: int = 100

    def __post_init__(self):
        valor = self.valor
        if not valor or valor.strip() == "":
            raise ValueError("El nombre de usuario no puede estar vacío")
        if len(valor.strip()) < self.MIN_LENGTH:
            raise ValueError(f"El nombre debe tener al menos {self.MIN_LENGTH} caracteres")
        if len(valor) > self.MAX_LENGTH:
            raise ValueError(f"El nombre no puede exceder {self.MAX_LENGTH} caracteres")


@dataclass(frozen=True)
class PasswordHash:
    """Value Object que envuelve un hash de contraseña (ya calculado en infraestructura)"""
    valor: str

    def __post_init__(self):
        if not self.valor or self.valor.strip() == "":
            raise ValueError("El hash de contraseña no puede estar vacío")