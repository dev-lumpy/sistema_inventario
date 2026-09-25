"""Entidad Producto (Aggregate Root)"""

from __future__ import annotations

from core.domain.producto.value_objects import (
    NombreProducto,
    Precio,
    Cantidad,
    StockMinimo,
    ProductoId,
)
from core.domain.usuario.value_objects import UsuarioId
from core.domain.producto.estado_stock import EstadoStock
from core.domain.producto.exceptions import (
    ProductoInactivoException,
    StockPorDebajoDelMinimoException,
    StockInsuficienteException,
)
from core.domain.shared.cantidad import Cantidad, StockInsuficienteError
from core.domain.shared.fecha import Fecha


class Producto:
    """Entidad raíz del agregado Producto"""

    def __init__(
        self,
        id: ProductoId,
        nombre: NombreProducto,
        precio: Precio,
        cantidad_inicial: Cantidad,
        stock_minimo: StockMinimo,
        vendedor_id: UsuarioId,
        categoria_id: str | None = None,
        activo: bool = True,
        fecha_creacion: Fecha | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad_inicial
        self.stock_minimo = stock_minimo
        self.vendedor_id = vendedor_id
        self.categoria_id = categoria_id
        self.activo = activo
        self.fecha_creacion = fecha_creacion or Fecha.ahora()

        # Regla: El stock inicial no puede ser menor al stock mínimo
        if self.cantidad.valor < self.stock_minimo.valor:
            raise StockPorDebajoDelMinimoException(
                self.cantidad.valor,
                self.stock_minimo.valor,
            )

    # ============ DERIVACIONES ============

    def estado_stock(self) -> EstadoStock:
        if self.cantidad.es_cero():
            return EstadoStock.AGOTADO
        if self.cantidad.es_menor_o_igual_que(self.stock_minimo):
            return EstadoStock.BAJO
        return EstadoStock.DISPONIBLE

    def esta_agotado(self) -> bool:
        return self.estado_stock() == EstadoStock.AGOTADO

    def esta_bajo_stock(self) -> bool:
        return self.estado_stock() == EstadoStock.BAJO

    def esta_disponible(self) -> bool:
        return self.estado_stock() == EstadoStock.DISPONIBLE

    def esta_en_alerta(self) -> bool:
        return self.estado_stock() in (EstadoStock.BAJO, EstadoStock.AGOTADO)

    # ============ MÉTODOS DE DOMINIO ============

    def actualizar_precio(self, nuevo_precio: Precio) -> None:
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        self.precio = nuevo_precio

    def aumentar_stock(self, cantidad: int) -> None:
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        if cantidad <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.cantidad = self.cantidad.sumar(cantidad)

    def reducir_stock(self, cantidad: int) -> None:
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        if cantidad <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        try:
            self.cantidad = self.cantidad.restar(cantidad)
        except StockInsuficienteError as e:
            raise StockInsuficienteException(disponible=e.disponible, solicitado=e.solicitado) from e

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def pertenece_a(self, usuario_id: UsuarioId) -> bool:
        return self.vendedor_id == usuario_id

    # ============ IDENTIDAD ============

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Producto):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Producto(id={self.id}, nombre='{self.nombre.valor}', "
            f"precio={self.precio.valor}, stock={self.cantidad.valor})"
        )