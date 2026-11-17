from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from core.domain.purchases.entities import Compra, Proveedor
from core.domain.purchases.enums import EstadoCompra


class ProveedorRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, proveedor_id: int) -> Proveedor | None:
        ...

    @abstractmethod
    def guardar(self, proveedor: Proveedor) -> Proveedor:
        ...

    @abstractmethod
    def listar_por_administrador(self, administrador_id: int) -> list[Proveedor]:
        ...

    @abstractmethod
    def eliminar(self, proveedor_id: int) -> None:
        ...


class CompraRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, compra_id: int) -> Compra | None:
        ...

    @abstractmethod
    def guardar(self, compra: Compra) -> Compra:
        ...

    @abstractmethod
    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        estado: EstadoCompra | None = None,
    ) -> list[Compra]:
        ...

    @abstractmethod
    def eliminar(self, compra_id: int) -> None:
        ...
