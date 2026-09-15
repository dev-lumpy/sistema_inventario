"""Repositorio en memoria para Producto (tests y desarrollo)"""

from __future__ import annotations

from typing import Optional
from core.domain.producto.producto import Producto
from core.domain.producto.repository import ProductoRepository
from core.domain.producto.value_objects import ProductoId
from core.domain.producto.estado_stock import EstadoStock


class ProductoRepositoryMemoria(ProductoRepository):
    def __init__(self):
        self._productos: dict[str, Producto] = {}

    def guardar(self, producto: Producto) -> None:
        self._productos[str(producto.id)] = producto

    def obtener_por_id(self, id: ProductoId) -> Optional[Producto]:
        return self._productos.get(str(id))

    def obtener_por_nombre(self, nombre: str) -> Optional[Producto]:
        for p in self._productos.values():
            if p.nombre.valor == nombre:
                return p
        return None

    def listar_todos(self) -> list[Producto]:
        return list(self._productos.values())

    def listar_por_categoria(self, categoria_id: str) -> list[Producto]:
        return [p for p in self._productos.values() if p.categoria_id == categoria_id]

    def listar_por_estado(self, estado: EstadoStock) -> list[Producto]:
        return [p for p in self._productos.values() if p.estado_stock() == estado]

    def buscar_por_texto(self, texto: str) -> list[Producto]:
        return [p for p in self._productos.values() if texto.lower() in p.nombre.valor.lower()]

    def listar_en_alerta(self) -> list[Producto]:
        return [p for p in self._productos.values() if p.esta_en_alerta()]

    def eliminar(self, id: ProductoId) -> None:
        self._productos.pop(str(id), None)