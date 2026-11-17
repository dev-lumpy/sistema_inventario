from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from core.domain.payments.entities import Pago


class PagoRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, pago_id: int) -> Pago | None:
        ...

    @abstractmethod
    def guardar(self, pago: Pago) -> Pago:
        ...

    @abstractmethod
    def listar_por_venta(self, venta_id: int) -> list[Pago]:
        ...

    @abstractmethod
    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[Pago]:
        ...

    @abstractmethod
    def eliminar(self, pago_id: int) -> None:
        ...
