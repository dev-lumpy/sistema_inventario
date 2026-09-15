"""Módulo Application - Casos de uso"""

from core.application.producto import (
    RegistrarProducto,
    RegistrarProductoInput,
    RegistrarProductoOutput,
    ConsultarInventario,
    ConsultarInventarioInput,
    ConsultarInventarioOutput,
    ObtenerProductosEnAlerta,
    ObtenerProductosEnAlertaOutput,
)
from core.application.movimiento_stock import (
    RegistrarEntradaStock,
    RegistrarEntradaStockInput,
    RegistrarEntradaStockOutput,
    RegistrarSalidaStock,
    RegistrarSalidaStockInput,
    RegistrarSalidaStockOutput,
    ObtenerHistorialMovimientos,
    ObtenerHistorialMovimientosInput,
    ObtenerHistorialMovimientosOutput,
)
from core.application.categoria import (
    CrearCategoria,
    CrearCategoriaInput,
    CrearCategoriaOutput,
    ListarCategorias,
    ListarCategoriasOutput,
)
from core.application.usuario import (
    AutenticarUsuario,
    AutenticarUsuarioInput,
    AutenticarUsuarioOutput,
)
from core.application.ports import (
    PasswordHasher,
    UnitOfWork,
)

__all__ = [
    'RegistrarProducto',
    'RegistrarProductoInput',
    'RegistrarProductoOutput',
    'ConsultarInventario',
    'ConsultarInventarioInput',
    'ConsultarInventarioOutput',
    'ObtenerProductosEnAlerta',
    'ObtenerProductosEnAlertaOutput',
    'RegistrarEntradaStock',
    'RegistrarEntradaStockInput',
    'RegistrarEntradaStockOutput',
    'RegistrarSalidaStock',
    'RegistrarSalidaStockInput',
    'RegistrarSalidaStockOutput',
    'ObtenerHistorialMovimientos',
    'ObtenerHistorialMovimientosInput',
    'ObtenerHistorialMovimientosOutput',
    'CrearCategoria',
    'CrearCategoriaInput',
    'CrearCategoriaOutput',
    'ListarCategorias',
    'ListarCategoriasOutput',
    'AutenticarUsuario',
    'AutenticarUsuarioInput',
    'AutenticarUsuarioOutput',
    'PasswordHasher',
    'UnitOfWork',
]