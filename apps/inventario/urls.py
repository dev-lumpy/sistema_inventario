# apps/inventario/urls.py
from django.urls import re_path
from .views import (
    index,
    CategoriaSelectAPIView,
    AddCategoriaAPIView,
    ProductoInsertAPIView,
    ProductoUpdateAPIView,
    ProductoAlertStockAPIView,
    ProductoSelectAPIView,
    ResumenHoyAPIView,
    RegistrarEntradaStockAPIView,
    MovimientoHistorialAPIView,
    ProductoSelectNameAPIView,
    ProductoHistoryMovimientosAPIView,
    ProveedorSelectAPIView,
    CategoriaDetailAPIView
)

urlpatterns = [
    re_path(r'^$', index, name="index"),
    re_path(r'^categorias/select/?$', CategoriaSelectAPIView.as_view(), name='categoria-select'),
    re_path(r'^productos/?$', ProductoInsertAPIView.as_view(), name='producto-insert'),
    re_path(r'^productos/select_all/?$', ProductoSelectAPIView.as_view(), name='producto-select'),
    re_path(r'^productos/alertas/?$', ProductoAlertStockAPIView.as_view(), name='producto-alert-stock'),
    re_path(r'^productos/(?P<pk>[^/]+)/?$', ProductoUpdateAPIView.as_view(), name='producto-update'),
    re_path(r'^proveedores/select/?$', ProveedorSelectAPIView.as_view(), name='proveedor-select'),
    re_path(r'^resumen/hoy/?$', ResumenHoyAPIView.as_view(), name='resumen-hoy'),

    # apps/inventario/urls.py
    re_path(r'^movimiento/entrada/?$', RegistrarEntradaStockAPIView.as_view(), name='movimiento-entrada'),

    # para el historial;
    re_path(r'^movimiento/entrada/historial/?$', MovimientoHistorialAPIView.as_view(), name='movimiento-historial'),
    re_path(r'^history_productos/?$', ProductoSelectNameAPIView.as_view(), name="productos-history"),
    re_path(r'^history_movimientos/?$', ProductoHistoryMovimientosAPIView.as_view(), name="productos-history-movimientos"),

    # para las categorias ya existe uno que hace devuelve todas las categorias
    re_path(r'^add_categoria/?$', AddCategoriaAPIView.as_view(), name='add-categoria'),
    re_path(r'^categorias/(?P<pk>\d+)/?$', CategoriaDetailAPIView.as_view(), name='categoria-detail'),
]
