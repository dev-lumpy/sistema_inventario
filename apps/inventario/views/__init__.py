from .prueba import index
from .categoria import (
    CategoriaSelectAPIView,
    AddCategoriaAPIView,
    CategoriaDetailAPIView
)
from .resumen import ResumenHoyAPIView
from .movimiento import (
    RegistrarEntradaStockAPIView,
    MovimientoHistorialAPIView,
)
from .proveedor import ProveedorSelectAPIView
from .producto import (
    ProductoInsertAPIView,
    ProductoSelectAPIView,
    ProductoSelectNameAPIView,
    ProductoUpdateAPIView,
    ProductoAlertStockAPIView,
    ProductoSelectNameAPIView,
    ProductoHistoryMovimientosAPIView
)

__all__ = [
    "ProveedorSelectAPIView",
    "RegistrarEntradaStockAPIView",
    "CategoriaSelectAPIView",
    "ProductoInsertAPIView",
    "ProductoUpdateAPIView",
    "ProductoAlertStockAPIView",
    "ProductoSelectNameAPIView",
    "ProductoSelectAPIView"

]
