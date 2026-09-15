"""Módulo Producto - Domain"""

# Entidad
from core.domain.producto.producto import Producto

# Value Objects
from core.domain.producto.value_objects import (
    ProductoId,
    NombreProducto,
    Precio,
    Cantidad,
    StockMinimo,
)

# Estado
from core.domain.producto.estado_stock import EstadoStock

# Excepciones
from core.domain.producto.exceptions import (
    ProductoIdInvalidoException,
    NombreProductoInvalidoException,
    CategoriaInvalidaException,
    PrecioInvalidoException,
    CantidadInvalidaException,
    StockMinimoInvalidoException,
    ProductoNoEncontradoException,
    ProductoDuplicadoException,
    StockInsuficienteException,
    ProductoInactivoException,
    StockPorDebajoDelMinimoException,
    CategoriaVaciaException,
)

# Repositorio
from core.domain.producto.repository import ProductoRepository

__all__ = [
    # Entidad
    'Producto',
    # Value Objects
    'ProductoId',
    'NombreProducto',
    'Precio',
    'Cantidad',
    'StockMinimo',
    # Estado
    'EstadoStock',
    # Excepciones
    'ProductoIdInvalidoException',
    'NombreProductoInvalidoException',
    'CategoriaInvalidaException',
    'PrecioInvalidoException',
    'CantidadInvalidaException',
    'StockMinimoInvalidoException',
    'ProductoNoEncontradoException',
    'ProductoDuplicadoException',
    'StockInsuficienteException',
    'ProductoInactivoException',
    'StockPorDebajoDelMinimoException',
    'CategoriaVaciaException',
    # Repositorio
    'ProductoRepository',
]