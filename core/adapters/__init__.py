"""Adaptadores - implementaciones de infraestructura en memoria"""

from core.adapters.repositories import (
    ProductoRepositoryMemoria,
    CategoriaRepositoryMemoria,
    MovimientoStockRepositoryMemoria,
    ProveedorRepositoryMemoria,
    UsuarioRepositoryMemoria,
)

__all__ = [
    "ProductoRepositoryMemoria",
    "CategoriaRepositoryMemoria",
    "MovimientoStockRepositoryMemoria",
    "ProveedorRepositoryMemoria",
    "UsuarioRepositoryMemoria",
]