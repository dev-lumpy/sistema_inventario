from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from core.domain.catalog.entities import (
    Categoria,
    MovimientoInventario,
    PrecioProducto,
    Producto,
)
from core.domain.shared.enums import TipoCliente


class CategoriaRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, categoria_id: int) -> Categoria | None:
        ...

    @abstractmethod
    def guardar(self, categoria: Categoria) -> Categoria:
        ...

    @abstractmethod
    def listar_por_administrador(self, administrador_id: int) -> list[Categoria]:
        ...

    @abstractmethod
    def eliminar(self, categoria_id: int) -> None:
        ...


class ProductoRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Producto | None:
        ...

    @abstractmethod
    def guardar(self, producto: Producto) -> Producto:
        ...

    @abstractmethod
    def listar_por_administrador(self, administrador_id: int) -> list[Producto]:
        ...

    @abstractmethod
    def buscar_por_nombre(
        self, administrador_id: int, texto: str
    ) -> list[Producto]:
        ...

    @abstractmethod
    def eliminar(self, producto_id: int) -> None:
        ...


class PrecioProductoRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, precio_id: int) -> PrecioProducto | None:
        ...

    @abstractmethod
    def obtener_vigente(
        self,
        producto_id: int,
        administrador_id: int,
        tipo_cliente: TipoCliente,
        momento: datetime | None = None,
    ) -> PrecioProducto | None:
        ...

    @abstractmethod
    def guardar(self, precio: PrecioProducto) -> PrecioProducto:
        ...

    @abstractmethod
    def listar_por_producto(
        self, producto_id: int, administrador_id: int
    ) -> list[PrecioProducto]:
        ...

    @abstractmethod
    def cerrar_vigencia(self, precio_id: int, momento: datetime | None = None) -> None:
        ...


class MovimientoInventarioRepository(ABC):
    @abstractmethod
    def guardar(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        ...

    @abstractmethod
    def listar_por_producto(
        self, producto_id: int, administrador_id: int
    ) -> list[MovimientoInventario]:
        ...

    @abstractmethod
    def listar_por_periodo(
        self, administrador_id: int, desde: datetime, hasta: datetime
    ) -> list[MovimientoInventario]:
        ...

    @abstractmethod
    def calcular_stock(self, producto_id: int, administrador_id: int) -> Decimal:
        ...
