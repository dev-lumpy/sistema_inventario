from .prueba import index
from .categoria import (
    CategoriaSelectAPIView,
    AddCategoriaAPIView,
    CategoriaDetailAPIView
)
from .resumen import ResumenHoyAPIView, ResumenPeriodoAPIView
from .movimiento import (
    RegistrarEntradaStockAPIView,
    MovimientoHistorialAPIView,
    RegistrarSalidaStockAPIView,
)
from .proveedor import ProveedorSelectAPIView
from .producto import (
    ProductoInsertAPIView,
    ProductoSelectAPIView,
    ProductoSelectNameAPIView,
    ProductoUpdateAPIView,
    ProductoAlertStockAPIView,
    ProductoSelectNameAPIView,
    ProductoHistoryMovimientosAPIView,
    ProductosMasVendidosView,
    ProductosVendidosEnRangoView,
)
from .reportes_pdf import ReportePeriodoPDFView

__all__ = [
    "ProveedorSelectAPIView",
    "RegistrarEntradaStockAPIView",
    "CategoriaSelectAPIView",
    "ProductoInsertAPIView",
    "ProductoUpdateAPIView",
    "ProductoAlertStockAPIView",
    "ProductoSelectNameAPIView",
    "ProductoSelectAPIView",
    "ProductosMasVendidosView",
    "ProductosVendidosEnRangoView",
    "ResumenPeriodoAPIView",
    "ReportePeriodoPDFView",
]
