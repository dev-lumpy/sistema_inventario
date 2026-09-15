"""Value Objects del dominio Proveedor"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import (
    ProveedorIdInvalidoException,
    NombreProveedorInvalidoException,
)


@dataclass(frozen=True)
class ProveedorId:
    """Value Object que identifica unívocamente a un Proveedor (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            try:
                object.__setattr__(self, "valor", UUID(self.valor))
            except (ValueError, AttributeError):
                raise ProveedorIdInvalidoException(str(self.valor))

    @classmethod
    def generar(cls) -> ProveedorId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> ProveedorId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"ProveedorId({self.valor})"


@dataclass(frozen=True)
class NombreProveedor:
    """Value Object que representa el nombre de un proveedor"""

    valor: str

    MIN_LENGTH: int = 3
    MAX_LENGTH: int = 80

    def __post_init__(self):
        valor = self.valor
        if not valor or valor.strip() == "":
            raise NombreProveedorInvalidoException(
                nombre=valor,
                razon="PROVEEDOR_NOMBRE_VACIO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )
        if len(valor.strip()) < self.MIN_LENGTH:
            raise NombreProveedorInvalidoException(
                nombre=valor,
                razon="PROVEEDOR_NOMBRE_CORTO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )
        if len(valor) > self.MAX_LENGTH:
            raise NombreProveedorInvalidoException(
                nombre=valor,
                razon="PROVEEDOR_NOMBRE_LARGO",
                min=self.MIN_LENGTH,
                max=self.MAX_LENGTH,
            )


@dataclass(frozen=True)
class ContactoProveedor:
    """Value Object opcional para contacto del proveedor"""

    valor: str

    MAX_LENGTH: int = 200

    def __post_init__(self):
        if not self.valor or self.valor.strip() == "":
            object.__setattr__(self, "valor", "")
        elif len(self.valor) > self.MAX_LENGTH:
            raise ValueError(f"El contacto no puede exceder {self.MAX_LENGTH} caracteres")