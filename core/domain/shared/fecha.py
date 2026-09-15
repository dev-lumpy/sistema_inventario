"""Value Object Fecha - envoltura inmutable de datetime con timezone UTC"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Fecha:
    """Value Object que representa una fecha/hora inmutable en UTC"""

    valor: datetime

    def __post_init__(self):
        """Normaliza a UTC, asigna UTC si no tiene timezone"""
        if self.valor.tzinfo is None:
            object.__setattr__(self, "valor", self.valor.replace(tzinfo=timezone.utc))
        else:
            object.__setattr__(self, "valor", self.valor.astimezone(timezone.utc))

    @classmethod
    def ahora(cls) -> Fecha:
        """Crea una Fecha con el momento actual en UTC"""
        return cls(datetime.now(timezone.utc))

    @classmethod
    def desde_iso(cls, iso_str: str) -> Fecha:
        """Crea una Fecha desde string ISO 8601"""
        return cls(datetime.fromisoformat(iso_str))

    def a_iso(self) -> str:
        """Retorna el valor como string ISO 8601"""
        return self.valor.isoformat()

    def es_antes_de(self, otra: Fecha) -> bool:
        return self.valor < otra.valor

    def es_despues_de(self, otra: Fecha) -> bool:
        return self.valor > otra.valor

    def __repr__(self) -> str:
        return f"Fecha({self.a_iso()})"