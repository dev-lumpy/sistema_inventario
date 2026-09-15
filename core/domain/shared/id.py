"""Value Object Id base - UUID v4"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Id:
    """Value Object base para identidades del dominio (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if not isinstance(self.valor, UUID):
            object.__setattr__(self, "valor", UUID(self.valor))

    @classmethod
    def generar(cls) -> Id:
        """Genera un nuevo UUID v4"""
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> Id:
        """Crea un Id desde un string UUID"""
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"Id({self.valor})"