"""Caso de uso: ConsultarInventario (RF-06, HU-03)"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.domain.producto.producto import Producto
from core.domain.producto.repository import ProductoRepository


@dataclass
class ConsultarInventarioInput:
    categoria_id: Optional[str] = None
    texto: Optional[str] = None


@dataclass
class ConsultarInventarioOutput:
    productos: list[Producto] = field(default_factory=list)


class ConsultarInventario:
    """Consulta el inventario con filtros opcionales"""

    def __init__(self, producto_repo: ProductoRepository):
        self._producto_repo = producto_repo

    def ejecutar(
        self, input: ConsultarInventarioInput
    ) -> ConsultarInventarioOutput:
        if input.categoria_id:
            productos = self._producto_repo.listar_por_categoria(
                input.categoria_id
            )
        elif input.texto:
            productos = self._producto_repo.buscar_por_texto(input.texto)
        else:
            productos = self._producto_repo.listar_todos()
        return ConsultarInventarioOutput(productos=productos)