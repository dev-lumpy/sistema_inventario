"""Entidad Producto (Aggregate Root)"""

from core.domain.producto.value_objects import (
    NombreProducto,
    CategoriaProducto,
    Precio,
    Cantidad,
    StockMinimo
)
from core.domain.producto.exceptions import (
    ProductoInactivoException,
    StockPorDebajoDelMinimoException,
    StockInsuficienteException
)
from core.i18n.message import MessageKey


class Producto:
    """Entidad raíz del dominio Producto"""
    
    def __init__(
        self,
        nombre: NombreProducto,
        categoria: CategoriaProducto,
        precio: Precio,
        cantidad_inicial: Cantidad,
        stock_minimo: StockMinimo,
        activo: bool = True
    ):
        # ============ ATRIBUTOS ============
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.cantidad = cantidad_inicial
        self.stock_minimo = stock_minimo
        self.activo = activo
        
        # ============ REGLAS DE NEGOCIO ============
        # Regla: El stock inicial no puede ser menor al stock mínimo
        if self.cantidad.valor < self.stock_minimo.valor:
            raise StockPorDebajoDelMinimoException(
                self.cantidad.valor,
                self.stock_minimo.valor
            )
    
    # ============ MÉTODOS DE DOMINIO ============
    
    def actualizar_precio(self, nuevo_precio: Precio) -> None:
        """Actualiza el precio del producto"""
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        self.precio = nuevo_precio
    
    def aumentar_stock(self, cantidad: int) -> None:
        """Aumenta el stock del producto (compra o reposición)"""
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        if cantidad <= 0:
            raise ValueError(MessageKey.PRODUCT_VALUE_ERROR)
        
        self.cantidad = self.cantidad.sumar(cantidad)
    
    def reducir_stock(self, cantidad: int) -> None:
        """Reduce el stock del producto (venta o consumo)"""
        if not self.activo:
            raise ProductoInactivoException(self.nombre.valor)
        if cantidad <= 0:
            raise ValueError(MessageKey.PRODUCT_DECREMENT_ERROR)
        
        self.cantidad = self.cantidad.restar(cantidad)
    
    def esta_en_alerta(self) -> bool:
        """Verifica si el producto está en stock mínimo (en alerta)"""
        return self.cantidad.valor <= self.stock_minimo.valor
    
    def activar(self) -> None:
        """Activa el producto"""
        self.activo = True
    
    def desactivar(self) -> None:
        """Desactiva el producto"""
        self.activo = False
    
    def __repr__(self) -> str:
        return (
            f"Producto(nombre='{self.nombre.valor}', "
            f"categoria='{self.categoria.valor}', "
            f"precio={self.precio.valor}, "
            f"stock={self.cantidad.valor})"
        )
