# core/domain/producto/exceptions.py

"""Excepciones del dominio Producto"""

from core.domain.exceptions import DomainException
from core.i18n.message import MessageKey


# ============================================
# EXCEPCIONES DE VALIDACIÓN
# ============================================

class ProductoIdInvalidoException(DomainException):
    """Se lanza cuando el ID del producto no es válido"""
    
    def __init__(self, id: str):
        super().__init__(
            code="PRODUCTO_ID_INVALIDO",
            message=f"ID de producto inválido: {id}",
            user_message_key=MessageKey.VALIDATION_INVALID,
            status_code=400,
            field="ID de producto",
            id=id
        )


class NombreProductoInvalidoException(DomainException):
    """Se lanza cuando el nombre no cumple con las reglas"""
    
    def __init__(self, nombre: str, razon: str, min: int, max: int):
        # Mapeo de razones a códigos específicos
        code_map = {
            MessageKey.NAME_EMPTY: "PRODUCTO_NOMBRE_VACIO",
            MessageKey.NAME_TOO_SHORT: "PRODUCTO_NOMBRE_CORTO",
            MessageKey.NAME_TOO_LONG: "PRODUCTO_NOMBRE_LARGO",
            MessageKey.NAME_SPECIAL_CHARS: "PRODUCTO_NOMBRE_CARACTERES_INVALIDOS",
            MessageKey.NAME_RESERVED: "PRODUCTO_NOMBRE_RESERVADO",
            MessageKey.NAME_STARTS_WITH_NUMBER: "PRODUCTO_NOMBRE_COMIENZA_CON_NUMERO",
        }
        
        super().__init__(
            code=code_map.get(razon, "PRODUCTO_NOMBRE_INVALIDO"),
            message=f"Nombre de producto inválido: {nombre}",
            user_message_key=razon,
            status_code=400,
            field=nombre,
            min=min,
            max=max
        )


class CategoriaInvalidaException(DomainException):
    """Se lanza cuando la categoría no está en el catálogo permitido"""
    
    def __init__(self, categoria: str, opciones: str):
        super().__init__(
            code="PRODUCTO_CATEGORIA_INVALIDA",
            message=f"Categoría inválida: {categoria}",
            user_message_key=MessageKey.VALIDATION_INVALID,
            status_code=400,
            field=categoria,
        )


class CategoriaVaciaException(DomainException):
    """Se lanza cuando la categoría está vacía"""
    
    def __init__(self):
        super().__init__(
            code="PRODUCTO_CATEGORIA_VACIA",
            message="La categoría no puede estar vacía",
            user_message_key=MessageKey.VALIDATION_INVALID,
            status_code=400,
            field="categoría"
        )


class PrecioInvalidoException(DomainException):
    """Se lanza cuando el precio es negativo o cero"""
    
    def __init__(self, precio: float, max_price: float = 999999.99):
        code     = ""
        user_key = ""
        if precio < 0:
            code = "PRODUCTO_PRECIO_NEGATIVO"
            user_key = MessageKey.PRICE_NEGATIVE
        elif precio == 0:
            code = "PRODUCTO_PRECIO_CERO"
            user_key = MessageKey.PRICE_NEGATIVE  # Reutilizamos el mensaje
        else:
            code = "PRODUCTO_PRECIO_EXCEDE_LIMITE"
            user_key = MessageKey.PRICE_TOO_HIGH
        
        super().__init__(
            code=code,
            message=f"Precio inválido: {precio}",
            user_message_key=user_key,
            status_code=400,
            price=precio,
            max_price=max_price
        )


class CantidadInvalidaException(DomainException):
    """Se lanza cuando la cantidad es negativa"""
    
    def __init__(self, cantidad: int):
        if cantidad < 0:
            code = "PRODUCTO_CANTIDAD_NEGATIVA"
            user_key = MessageKey.STOCK_NEGATIVE
        else:
            code = "PRODUCTO_CANTIDAD_CERO"
            user_key = MessageKey.STOCK_ZERO
        
        super().__init__(
            code=code,
            message=f"Cantidad inválida: {cantidad}",
            user_message_key=user_key,
            status_code=400,
            cantidad=cantidad
        )


class StockMinimoInvalidoException(DomainException):
    """Se lanza cuando el stock mínimo es negativo"""
    
    def __init__(self, minimo: int):
        super().__init__(
            code="PRODUCTO_STOCK_MINIMO_NEGATIVO",
            message=f"Stock mínimo inválido: {minimo}",
            user_message_key=MessageKey.STOCK_NEGATIVE,
            status_code=400,
            stock=minimo
        )


# ============================================
# EXCEPCIONES DE REGLAS DE NEGOCIO
# ============================================

class StockPorDebajoDelMinimoException(DomainException):
    """Se lanza cuando el stock actual está por debajo del mínimo"""
    
    def __init__(self, stock_actual: int, stock_minimo: int):
        super().__init__(
            code="PRODUCTO_STOCK_BAJO_MINIMO",
            message=f"Stock actual ({stock_actual}) está por debajo del mínimo ({stock_minimo})",
            user_message_key=MessageKey.STOCK_BELOW_MINIMUM,
            status_code=400,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo
        )


class ProductoNoEncontradoException(DomainException):
    """Se lanza cuando no se encuentra un producto por ID"""
    
    def __init__(self, product_id: str):
        super().__init__(
            code="PRODUCTO_NOT_FOUND",
            message=f"Producto no encontrado: {product_id}",
            user_message_key=MessageKey.PRODUCT_NOT_FOUND,
            status_code=404,
            product_id=product_id
        )


class ProductoDuplicadoException(DomainException):
    """Se lanza cuando intentas crear un producto con nombre duplicado"""
    
    def __init__(self, nombre: str):
        super().__init__(
            code="PRODUCTO_DUPLICADO",
            message=f"Producto duplicado: {nombre}",
            user_message_key=MessageKey.NAME_DUPLICATED,
            status_code=409,
            field=nombre
        )


class StockInsuficienteException(DomainException):
    """Se lanza cuando intentas vender más stock del disponible"""
    
    def __init__(self, disponible: int, solicitado: int):
        super().__init__(
            code="PRODUCTO_STOCK_INSUFICIENTE",
            message=f"Stock insuficiente. Disponible: {disponible}, Solicitado: {solicitado}",
            user_message_key=MessageKey.STOCK_INSUFFICIENT,
            status_code=409,
            available=disponible,
            requested=solicitado
        )


class ProductoInactivoException(DomainException):
    """Se lanza cuando intentas operar con un producto inactivo"""
    
    def __init__(self, nombre: str):
        super().__init__(
            code="PRODUCTO_INACTIVO",
            message=f"Producto inactivo: {nombre}",
            user_message_key=MessageKey.PRODUCT_INACTIVE_ACTION,
            status_code=403,
            entity=nombre
        )


# ============================================
# EXCEPCIONES ADICIONALES (las que "faltaban")
# ============================================

class ProductoConStockNegativoException(DomainException):
    """Se lanza cuando el stock queda en negativo (error de consistencia)"""
    
    def __init__(self, producto_id: str, stock_actual: int):
        super().__init__(
            code="PRODUCTO_STOCK_NEGATIVO",
            message=f"El producto {producto_id} tiene stock negativo: {stock_actual}",
            user_message_key=MessageKey.STOCK_NEGATIVE,
            status_code=500,
            stock=stock_actual,
            producto_id=producto_id
        )


class ProductoConPrecioCeroException(DomainException):
    """Se lanza cuando el precio es cero (puede ser permitido o no según negocio)"""
    
    def __init__(self, nombre: str):
        super().__init__(
            code="PRODUCTO_PRECIO_CERO",
            message=f"El producto '{nombre}' tiene precio cero",
            user_message_key=MessageKey.PRICE_NEGATIVE,
            status_code=400,
            field=nombre
        )


class ProductoConCategoriaNoPermitidaException(DomainException):
    """Se lanza cuando la categoría no está permitida para este tipo de producto"""
    
    def __init__(self, categoria: str, producto: str):
        super().__init__(
            code="PRODUCTO_CATEGORIA_NO_PERMITIDA",
            message=f"Categoría '{categoria}' no permitida para '{producto}'",
            user_message_key=MessageKey.VALIDATION_INVALID,
            status_code=400,
            field=f"categoría '{categoria}'",
            producto=producto
        )
