from __future__ import annotations

from types import TracebackType

from django.db import transaction

from core.application.ports.unit_of_work import UnitOfWork

from apps.accounts.repositories import (
    DjangoAdministradorRepository,
    DjangoUsuarioRepository,
    DjangoVendedorRepository,
    DjangoVinculoRepository,
)
from apps.catalog.repositories import (
    DjangoCategoriaRepository,
    DjangoMovimientoInventarioRepository,
    DjangoPrecioProductoRepository,
    DjangoProductoRepository,
)
from apps.payments.repositories import DjangoPagoRepository
from apps.purchases.repositories import (
    DjangoCompraRepository,
    DjangoProveedorRepository,
)
from apps.sales.repositories import DjangoVentaRepository


class DjangoUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.usuarios = DjangoUsuarioRepository()
        self.administradores = DjangoAdministradorRepository(self.usuarios)
        self.vendedores = DjangoVendedorRepository(self.usuarios)
        self.vinculos = DjangoVinculoRepository()
        self.categorias = DjangoCategoriaRepository()
        self.productos = DjangoProductoRepository()
        self.precios = DjangoPrecioProductoRepository()
        self.movimientos = DjangoMovimientoInventarioRepository()
        self.ventas = DjangoVentaRepository()
        self.proveedores = DjangoProveedorRepository()
        self.compras = DjangoCompraRepository()
        self.pagos = DjangoPagoRepository()
        self._atomic = None

    def __enter__(self) -> DjangoUnitOfWork:
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
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
        if self._atomic is not None:
            self._atomic.__exit__(exc_type, exc, tb)
        return False

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        transaction.set_rollback(True)
