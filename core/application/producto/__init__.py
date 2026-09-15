"""Módulo Application - Producto"""

from core.application.producto.registrar_producto import (
    RegistrarProducto,
    RegistrarProductoInput,
    RegistrarProductoOutput,
)
from core.application.producto.consultar_inventario import (
    ConsultarInventario,
    ConsultarInventarioInput,
    ConsultarInventarioOutput,
)
from core.application.producto.obtener_productos_en_alerta import (
    ObtenerProductosEnAlerta,
    ObtenerProductosEnAlertaOutput,
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
]