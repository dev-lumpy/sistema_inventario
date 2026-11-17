from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from core.application.ports.accounts import (
    AdministradorRepository,
    UsuarioRepository,
    VendedorRepository,
    VinculoRepository,
)
from core.application.ports.catalog import (
    CategoriaRepository,
    MovimientoInventarioRepository,
    PrecioProductoRepository,
    ProductoRepository,
)
from core.application.ports.payments import PagoRepository
from core.application.ports.purchases import CompraRepository, ProveedorRepository
from core.application.ports.sales import VentaRepository


class UnitOfWork(ABC):
    usuarios: UsuarioRepository
    administradores: AdministradorRepository
    vendedores: VendedorRepository
    vinculos: VinculoRepository
    categorias: CategoriaRepository
    productos: ProductoRepository
    precios: PrecioProductoRepository
    movimientos: MovimientoInventarioRepository
    ventas: VentaRepository
    proveedores: ProveedorRepository
    compras: CompraRepository
    pagos: PagoRepository

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
