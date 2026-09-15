"""Interfaz del repositorio de Producto (puerto de dominio)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.domain.producto.producto import Producto
from core.domain.producto.value_objects import ProductoId
from core.domain.producto.estado_stock import EstadoStock


class ProductoRepository(ABC):
    """Puerto secundario: persistencia de Productos"""

    @abstractmethod
    def guardar(self, producto: Producto) -> None:
        """Guarda o actualiza un producto"""
        ...

    @abstractmethod
    def obtener_por_id(self, id: ProductoId) -> Optional[Producto]:
        """Obtiene un producto por su ID"""
        ...

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Producto]:
        """Obtiene un producto por su nombre exacto"""
        ...

    @abstractmethod
    def listar_todos(self) -> list[Producto]:
        """Lista todos los productos"""
        ...

    @abstractmethod
    def listar_por_categoria(self, categoria_id: str) -> list[Producto]:
        """Lista productos por categoría"""
        ...

    @abstractmethod
    def listar_por_estado(self, estado: EstadoStock) -> list[Producto]:
        """Lista productos según su estado de stock"""
        ...

    @abstractmethod
    def buscar_por_texto(self, texto: str) -> list[Producto]:
        """Busca productos cuyo nombre contenga el texto"""
        ...

    @abstractmethod
    def listar_en_alerta(self) -> list[Producto]:
        """Lista productos cuyo stock está por debajo del mínimo"""
        ...

    @abstractmethod
    def eliminar(self, id: ProductoId) -> None:
        """Elimina un producto por su ID"""
        ...