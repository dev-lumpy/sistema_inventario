 # core/i18n/catalogs/products.py
from .base import Language, MessageKey


class ProductsES(MessageKey):
    LANGUAGE = Language.SPANISH

    NOT_FOUND = "El producto con ID '{product_id}' no existe"
    ALREADY_EXISTS = "El producto con ID '{product_id}' ya existe"
    VALUE_ERROR = "La cantidad a aumentar debe ser positiva"
    DECREMENT_ERROR = "La cantidad a reducir debe ser positiva"
    INACTIVE_ACTION = "No se permiten acciones para {entity}, porque es un producto inactivo"
    NEGATIVE_OPERATION = "No se puede sumar o restar una cantidad negativa"


class ProductsEN(ProductsES):
    LANGUAGE = Language.ENGLISH

    NOT_FOUND = "Product with ID '{product_id}' not found"
    ALREADY_EXISTS = "Product with ID '{product_id}' already exists"
    VALUE_ERROR = "The amount to increase must be positive"
    DECREMENT_ERROR = "The amount to decrease must be positive"
    INACTIVE_ACTION = "Actions are not allowed for {entity}, because it is an inactive product"
    NEGATIVE_OPERATION = "Cannot add or subtract a negative amount"


# Registro de esta entidad
ENTITY = "product"
CATALOGS = {
    Language.SPANISH: ProductsES,
    Language.ENGLISH: ProductsEN,
}
