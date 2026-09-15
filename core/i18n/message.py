# core/i18n/message.py

"""Catálogo de mensajes multilenguaje"""

from typing import Dict, Any
from enum import Enum

class Language:
    SPANISH = "es"
    ENGLISH = "en"
    # Agregar más idiomas aquí

class MessageKey:
    """Llaves de mensajes para cada error"""

    # Razones específicas para nombres inválidos
    NAME_EMPTY = "name.empty"
    NAME_TOO_SHORT = "name.too_short"
    NAME_TOO_LONG = "name.too_long"
    NAME_SPECIAL_CHARS = "name.special_chars"
    NAME_RESERVED = "name.reserved"
    NAME_STARTS_WITH_NUMBER = "name.starts_with_number"
    NAME_DUPLICATED = "name.duplicated"
    NAME_ALREADY_USED = "name.already_used"
    
    # Razones específicas para préstamos
    BORROW_LIMIT_EXCEEDED = "borrow.limit_exceeded"
    BORROW_USER_BLOCKED = "borrow.user_blocked"
    BORROW_BOOK_UNAVAILABLE = "borrow.book_unavailable"
    BORROW_BOOK_RESERVED = "borrow.book_reserved"
    BORROW_HAS_DEBTS = "borrow.has_debts"
    BORROW_TOO_MANY_LOANS = "borrow.too_many_loans"
    
    # Stock
    STOCK_NEGATIVE = "stock.negative"
    STOCK_EXCEEDS_LIMIT = "stock.exceeds_limit"
    STOCK_INSUFFICIENT = "stock.insufficient"
    STOCK_ZERO = "stock.zero"
    STOCK_BELOW_MINIMUM = "stock.below_minimum"
    
    # Validation
    VALIDATION_INVALID = "validation.invalid"
    NAME_INVALID = "name.invalid"
    
    # Entity
    ENTITY_NOT_FOUND = "entity.not_found"
    
    # Price
    PRICE_NEGATIVE = "price.negative"
    PRICE_TOO_HIGH = "price.too_high"
    
    # Email
    EMAIL_INVALID = "email.invalid"
    EMAIL_ALREADY_EXISTS = "email.already_exists"
    
    # Product
    PRODUCT_NOT_FOUND = "product.not_found"
    PRODUCT_ALREADY_EXISTS = "product.already_exists"
    PRODUCT_VALUE_ERROR = "producto.value_error"
    PRODUCT_DECREMENT_ERROR = "product.decrement_error"
    PRODUCT_INACTIVE_ACTION = "product.inactive_action"
    PRODUCT_NEGATIVE_OPERATION = "product.negative_operation"
    
    # Permission
    PERMISSION_DENIED = "permission.denied"
    
    # State
    STATE_INVALID = "state.invalid"
    
    # Conflict
    CONFLICT_GENERIC = "conflict.generic"
    
    # Business Rule
    BUSINESS_RULE_VIOLATION = "business.rule_violation"
    USER_CANNOT_BORROW = "user.cannot_borrow"
    
    # User
    USER_NOT_FOUND = "user.not_found"
    USER_ALREADY_EXISTS = "user.already_exists"
    USER_INACTIVE = "user.inactive"
    
    # Order
    ORDER_NOT_FOUND = "order.not_found"
    ORDER_EMPTY = "order.empty"
    ORDER_INVALID_STATE = "order.invalid_state"


# Diccionario de mensajes por idioma
MESSAGES: Dict[str, Dict[str, str]] = {
    Language.SPANISH: {
        # Stock
        MessageKey.STOCK_NEGATIVE: "El stock no puede ser negativo",
        MessageKey.STOCK_EXCEEDS_LIMIT: "El stock {current} excede el límite de {limit}",
        MessageKey.STOCK_INSUFFICIENT: "Stock insuficiente. Disponible: {available}, Solicitado: {requested}",
        MessageKey.STOCK_ZERO: "El stock no puede ser cero",
        MessageKey.STOCK_BELOW_MINIMUM: "El stock {current} está por debajo del mínimo {minimum}",
        
        # Validation
        MessageKey.VALIDATION_INVALID: "La categoria '{field}' no es válido",
        MessageKey.NAME_INVALID: "El nombre '{field}' no es válido",
        
        # Entity
        MessageKey.ENTITY_NOT_FOUND: "No encontramos el {entity_type} que buscas",
        
        # Price
        MessageKey.PRICE_NEGATIVE: "El precio no puede ser negativo",
        MessageKey.PRICE_TOO_HIGH: "El precio {price} excede el límite de {max_price}",
        
        # Email
        MessageKey.EMAIL_INVALID: "El email '{email}' no es válido",
        MessageKey.EMAIL_ALREADY_EXISTS: "El email '{email}' ya está registrado",
        
        # Product
        MessageKey.PRODUCT_NOT_FOUND: "El producto con ID '{product_id}' no existe",
        MessageKey.PRODUCT_ALREADY_EXISTS: "El producto con ID '{product_id}' ya existe",
        MessageKey.PRODUCT_VALUE_ERROR: "La cantidad a aumentar debe ser positiva",
        MessageKey.PRODUCT_DECREMENT_ERROR: "La cantidad a reducir debe ser positiva",
        MessageKey.PRODUCT_INACTIVE_ACTION: "No se permiten acciones para {entity}, porque es un producto que está inactivo",
        MessageKey.PRODUCT_NEGATIVE_OPERATION: "No se puede sumar o restar una cantidad negativa",
        
        # User
        MessageKey.USER_NOT_FOUND: "El usuario con ID '{user_id}' no existe",
        MessageKey.USER_ALREADY_EXISTS: "El usuario '{email}' ya existe",
        MessageKey.USER_INACTIVE: "El usuario '{user_id}' está inactivo",
        
        # Order
        MessageKey.ORDER_NOT_FOUND: "La orden '{order_id}' no existe",
        MessageKey.ORDER_EMPTY: "La orden no puede estar vacía",
        MessageKey.ORDER_INVALID_STATE: "Estado inválido: {current_state}, se requiere {required_state}",
        
        # Permission
        MessageKey.PERMISSION_DENIED: "No tienes permiso para realizar esta acción",
        
        # State
        MessageKey.STATE_INVALID: "La {entity} no está en un estado válido",
        
        # Conflict
        MessageKey.CONFLICT_GENERIC: "Conflicto con los datos actuales",
        
        # Business Rule
        MessageKey.BUSINESS_RULE_VIOLATION: "Operación no permitida por reglas de negocio",
        MessageKey.USER_CANNOT_BORROW: "No puedes pedir prestado: {reason}",

        # Business Rule
        MessageKey.BUSINESS_RULE_VIOLATION: "Operación no permitida por las reglas de negocio",
        MessageKey.USER_CANNOT_BORROW: "No puedes pedir prestado: {reason}",
        
        # Razones específicas para nombres inválidos
        MessageKey.NAME_EMPTY: "El nombre no puede estar vacío",
        MessageKey.NAME_TOO_SHORT: "El nombre '{field}' es demasiado corto (mínimo {min} caracteres)",
        MessageKey.NAME_TOO_LONG: "El nombre '{field}' es demasiado largo (máximo {max} caracteres)",
        MessageKey.NAME_SPECIAL_CHARS: "El nombre '{field}' contiene caracteres no permitidos",
        MessageKey.NAME_RESERVED: "El nombre '{field}' está reservado",
        MessageKey.NAME_STARTS_WITH_NUMBER: "El nombre '{field}' no puede empezar con números",
        MessageKey.NAME_DUPLICATED: "El nombre '{field}' ya está en uso",
        MessageKey.NAME_ALREADY_USED: "El nombre '{field}' ya fue utilizado anteriormente",
        
        # Razones específicas para préstamos
        MessageKey.BORROW_LIMIT_EXCEEDED: "Límite de préstamos excedido (máximo {limit})",
        MessageKey.BORROW_USER_BLOCKED: "Usuario bloqueado: {reason}",
        MessageKey.BORROW_BOOK_UNAVAILABLE: "El libro no está disponible para préstamo",
        MessageKey.BORROW_BOOK_RESERVED: "El libro está reservado para otro usuario hasta {date}",
        MessageKey.BORROW_HAS_DEBTS: "Tienes deudas pendientes de {amount}€",
        MessageKey.BORROW_TOO_MANY_LOANS: "Tienes demasiados préstamos activos ({count}/{max})",
    },
    
    Language.ENGLISH: {
        # Conflict
        MessageKey.CONFLICT_GENERIC: "Conflict with current data",
        
        # Business Rule
        MessageKey.BUSINESS_RULE_VIOLATION: "Operation not allowed by business rules",
        MessageKey.USER_CANNOT_BORROW: "Cannot borrow: {reason}",
        
        # Razones específicas para nombres inválidos
        MessageKey.NAME_EMPTY: "Name cannot be empty",
        MessageKey.NAME_TOO_SHORT: "Name '{field}' is too short (minimum {min} characters)",
        MessageKey.NAME_TOO_LONG: "Name '{field}' is too long (maximum {max} characters)",
        MessageKey.NAME_SPECIAL_CHARS: "Name '{field}' contains invalid characters",
        MessageKey.NAME_RESERVED: "Name '{field}' is reserved",
        MessageKey.NAME_STARTS_WITH_NUMBER: "Name '{field}' cannot start with numbers",
        MessageKey.NAME_DUPLICATED: "Name '{field}' is already in use",
        MessageKey.NAME_ALREADY_USED: "Name '{field}' was previously used",
        
        # Razones específicas para préstamos
        MessageKey.BORROW_LIMIT_EXCEEDED: "Borrow limit exceeded (maximum {limit})",
        MessageKey.BORROW_USER_BLOCKED: "User blocked: {reason}",
        MessageKey.BORROW_BOOK_UNAVAILABLE: "Book is not available for borrowing",
        MessageKey.BORROW_BOOK_RESERVED: "Book is reserved for another user until {date}",
        MessageKey.BORROW_HAS_DEBTS: "You have outstanding debts of {amount}€",
        MessageKey.BORROW_TOO_MANY_LOANS: "You have too many active loans ({count}/{max})",
        
        # Stock
        MessageKey.STOCK_NEGATIVE: "Stock cannot be negative",
        MessageKey.STOCK_EXCEEDS_LIMIT: "Stock {current} exceeds the limit of {limit}",
        MessageKey.STOCK_INSUFFICIENT: "Insufficient stock. Available: {available}, Requested: {requested}",
        MessageKey.STOCK_ZERO: "Stock cannot be zero",
        MessageKey.STOCK_BELOW_MINIMUM: "Stock {current} is below the minimum {minimum}",
        
        # Validation
        MessageKey.VALIDATION_INVALID: "The category '{field}' is invalid",
        MessageKey.NAME_INVALID: "The name '{field}' is not valid",
        
        # Entity
        MessageKey.ENTITY_NOT_FOUND: "We could not find the {entity_type} you are looking for",
        
        # Price
        MessageKey.PRICE_NEGATIVE: "Price cannot be negative",
        MessageKey.PRICE_TOO_HIGH: "Price {price} exceeds the limit of {max_price}",
        
        # Email
        MessageKey.EMAIL_INVALID: "Invalid email '{email}'",
        MessageKey.EMAIL_ALREADY_EXISTS: "Email '{email}' already registered",
        
        # Product
        MessageKey.PRODUCT_NOT_FOUND: "Product with ID '{product_id}' not found",
        MessageKey.PRODUCT_ALREADY_EXISTS: "Product with ID '{product_id}' already exists",
        MessageKey.PRODUCT_VALUE_ERROR: "The amount to increase must be positive",
        MessageKey.PRODUCT_DECREMENT_ERROR: "The amount to decrease must be positive",
        MessageKey.PRODUCT_INACTIVE_ACTION: "Actions are not allowed for {entity}, because it is an inactive product",
        MessageKey.PRODUCT_NEGATIVE_OPERATION: "Cannot add or subtract a negative amount",
        
        # User
        MessageKey.USER_NOT_FOUND: "User with ID '{user_id}' not found",
        MessageKey.USER_ALREADY_EXISTS: "User '{email}' already exists",
        MessageKey.USER_INACTIVE: "User '{user_id}' is inactive",
        
        # Order
        MessageKey.ORDER_NOT_FOUND: "Order '{order_id}' not found",
        MessageKey.ORDER_EMPTY: "Order cannot be empty",
        MessageKey.ORDER_INVALID_STATE: "Invalid state: {current_state}, required: {required_state}",
        
        # Permission
        MessageKey.PERMISSION_DENIED: "You don't have permission to perform this action",
        
        # State
        MessageKey.STATE_INVALID: "The {entity} is not in a valid state",
        
        # Conflict
        MessageKey.CONFLICT_GENERIC: "Conflict with current data",
        
        # Business Rule
        MessageKey.BUSINESS_RULE_VIOLATION: "Operation not allowed by business rules",
        MessageKey.USER_CANNOT_BORROW: "Cannot borrow: {reason}",
    }
}
