"""Caso de uso: RegistrarProducto (RF-01, HU-01)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.domain.producto.producto import Producto
from core.domain.producto.repository import ProductoRepository
from core.domain.producto.value_objects import (
    ProductoId,
    NombreProducto,
    Precio,
    Cantidad,
    StockMinimo,
)
from core.domain.usuario.value_objects import UsuarioId
from core.domain.shared.fecha import Fecha


@dataclass
class RegistrarProductoInput:
    nombre: str
    precio: float
    cantidad_inicial: int
    stock_minimo: int
    vendedor_id: str
    categoria_id: Optional[str] = None


@dataclass
class RegistrarProductoOutput:
    producto_id: str


class RegistrarProducto:
    """Registra un nuevo producto en el sistema"""

    def __init__(self, producto_repo: ProductoRepository):
        self._producto_repo = producto_repo

    def ejecutar(self, input: RegistrarProductoInput) -> RegistrarProductoOutput:
        producto = Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto(input.nombre),
            precio=Precio(input.precio),
            cantidad_inicial=Cantidad(input.cantidad_inicial),
            stock_minimo=StockMinimo(input.stock_minimo),
            vendedor_id=UsuarioId.desde_str(input.vendedor_id),
            categoria_id=input.categoria_id,
            fecha_creacion=Fecha.ahora(),
        )
        self._producto_repo.guardar(producto)
        return RegistrarProductoOutput(producto_id=str(producto.id))