"""Módulo Domain - Todos los dominios"""

from core.domain.producto import (
    Producto,
    NombreProducto,
    CategoriaProducto,
    Precio,
    Cantidad,
    StockMinimo,
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
    'Producto',
    'NombreProducto',
    'CategoriaProducto',
    'Precio',
    'Cantidad',
    'StockMinimo',
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
