# core/domain/producto/value_objects.py
"""Value Objects del dominio Producto"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .exceptions import (
    CategoriaVaciaException,
    ProductoIdInvalidoException,
    NombreProductoInvalidoException,
    CategoriaInvalidaException,
    PrecioInvalidoException,
    CantidadInvalidaException,
    StockMinimoInvalidoException,
    StockInsuficienteException,
    StockPorDebajoDelMinimoException,
    ProductoConPrecioCeroException,
    ProductoConCategoriaNoPermitidaException,
)
from core.i18n.message import MessageKey

# ============================================
# 2. Value Objects
# ============================================


@dataclass(frozen=True)
class NombreProducto:
    """Value Object que representa el nombre de un producto"""

    valor: str
    
    MIN_LENGTH: int = 3
    MAX_LENGTH: int = 50
    NOMBRES_RESERVADOS: tuple = ("admin", "root", "system", "test")
    
    def __post_init__(self):
        """Valida el nombre al momento de la creación"""
        valor = self.valor
        min_len = self.MIN_LENGTH
        max_len = self.MAX_LENGTH
        
        # Comparación: ¿El nombre está vacío o solo tiene espacios?
        if not valor or valor.strip() == "":
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_EMPTY,
                min=min_len,
                max=max_len
            )
        
        # Comparación: ¿El nombre tiene menos de 3 caracteres?
        if len(valor) < min_len:
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_TOO_SHORT,
                min=min_len,
                max=max_len
            )
        
        # Comparación: ¿El nombre tiene más de 50 caracteres?
        if len(valor) > max_len:
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_TOO_LONG,
                min=min_len,
                max=max_len
            )
        
        # Comparación: ¿El nombre contiene caracteres especiales?
        if not valor.replace(" ", "").isalnum():
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_SPECIAL_CHARS,
                min=min_len,
                max=max_len
            )
        
        # Comparación: ¿El nombre es una palabra reservada?
        if valor.lower() in self.NOMBRES_RESERVADOS:
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_RESERVED,
                min=min_len,
                max=max_len
            )
        
        # Comparación: ¿El nombre comienza con un número?
        if valor[0].isdigit():
            raise NombreProductoInvalidoException(
                nombre=valor,
                razon=MessageKey.NAME_STARTS_WITH_NUMBER,
                min=min_len,
                max=max_len
            )

# 2. CategoriaProducto - Valida categoría
@dataclass(frozen=True)
class CategoriaProducto:
    """Categoría de producto (solo valida que no esté vacía)"""
    valor: str
    
    def __post_init__(self):
        if not self.valor or self.valor.strip() == "":
            raise CategoriaVaciaException()

# 3. Precio - Valida precio
@dataclass(frozen=True)
class Precio:
    valor: float
    
    def __post_init__(self):
        if self.valor <= 0:
            raise PrecioInvalidoException(self.valor)

# 4. Cantidad - Valida stock
@dataclass(frozen=True)
class Cantidad:
    """Cantidad de productos (stock)"""
    valor: int
    
    def __post_init__(self):
        """Valida que la cantidad no sea negativa"""
        if self.valor < 0:
            raise CantidadInvalidaException(cantidad=self.valor)
    
    # ============ OPERACIONES ============
    def sumar(self, cantidad: int) -> Cantidad:
        """Suma una cantidad y retorna un nuevo Value Object"""
        if cantidad < 0:
            raise ValueError(MessageKey.PRODUCT_NEGATIVE_OPERATION)
        return Cantidad(self.valor + cantidad)
    
    def restar(self, cantidad: int) -> Cantidad:
        """Resta una cantidad y retorna un nuevo Value Object"""
        if cantidad < 0:
            raise ValueError(MessageKey.PRODUCT_NEGATIVE_OPERATION)
        
        nuevo_valor = self.valor - cantidad
        if nuevo_valor < 0:
            raise StockInsuficienteException(
                disponible=self.valor,
                solicitado=cantidad
            )
        return Cantidad(nuevo_valor)
    
    # ============ COMPARACIONES ============
    def es_menor_que(self, otra: Cantidad) -> bool:
        return self.valor < otra.valor
    
    def es_mayor_que(self, otra: Cantidad) -> bool:
        return self.valor > otra.valor
    
    def es_menor_o_igual_que(self, otra: Cantidad) -> bool:
        return self.valor <= otra.valor
    
    def es_mayor_o_igual_que(self, otra: Cantidad) -> bool:
        return self.valor >= otra.valor
    
    # ============ UTILIDADES ============
    def es_cero(self) -> bool:
        return self.valor == 0
    
    def es_positivo(self) -> bool:
        return self.valor > 0
    
    def __str__(self) -> str:
        return str(self.valor)

# 5. StockMinimo - Valida mínimo
@dataclass(frozen=True)
class StockMinimo:
    valor: int
    
    def __post_init__(self):
        if self.valor < 0:
            raise StockMinimoInvalidoException(self.valor)
        
