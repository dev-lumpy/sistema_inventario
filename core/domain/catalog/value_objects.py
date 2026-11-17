from __future__ import annotations

from dataclasses import dataclass

from core.domain.shared.validators import texto_requerido


@dataclass(frozen=True)
class NombreCategoria:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_requerido(self.valor, "categoría", 100))


@dataclass(frozen=True)
class NombreProducto:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", texto_requerido(self.valor, "producto", 200))
