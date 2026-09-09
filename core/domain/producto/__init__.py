"""Módulo Producto - Domain"""

# Entidad
from core.domain.producto.producto import Producto

# Value Objects
from core.domain.producto.value_objects import (
    NombreProducto,
    CategoriaProducto,
    Precio,
    Cantidad,
    StockMinimo
)

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
    ProductoInactivoException
)

__all__ = [
    # Entidad
    'Producto',
    
    # Value Objects
    'NombreProducto',
    'CategoriaProducto',
    'Precio',
    'Cantidad',
    'StockMinimo',
    
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
    'ProductoInactivoException'
]
