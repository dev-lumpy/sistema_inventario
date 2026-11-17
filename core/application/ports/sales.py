from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from core.domain.sales.entities import Venta
from core.domain.sales.enums import EstadoVenta


class VentaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, venta_id: int) -> Venta | None:
        ...

    @abstractmethod
    def guardar(self, venta: Venta) -> Venta:
        ...

    @abstractmethod
    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        estado: EstadoVenta | None = None,
    ) -> list[Venta]:
        ...

    @abstractmethod
    def eliminar(self, venta_id: int) -> None:
        ...
