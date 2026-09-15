"""Adaptadores de repositorio en memoria - para tests y desarrollo"""

from core.adapters.repositories.producto_repository_memoria import (
    ProductoRepositoryMemoria,
)
from core.adapters.repositories.categoria_repository_memoria import (
    CategoriaRepositoryMemoria,
)
from core.adapters.repositories.movimiento_repository_memoria import (
    MovimientoStockRepositoryMemoria,
)
from core.adapters.repositories.proveedor_repository_memoria import (
    ProveedorRepositoryMemoria,
)
from core.adapters.repositories.usuario_repository_memoria import (
    UsuarioRepositoryMemoria,
)

__all__ = [
    "ProductoRepositoryMemoria",
    "CategoriaRepositoryMemoria",
    "MovimientoStockRepositoryMemoria",
    "ProveedorRepositoryMemoria",
    "UsuarioRepositoryMemoria",
]