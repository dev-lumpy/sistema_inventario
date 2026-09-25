 # core/i18n/catalogs/name.py
from .base import Language, MessageKey


class NameES(MessageKey):
    LANGUAGE = Language.SPANISH

    EMPTY = "El nombre de usuario no puede estar vacío"
    TOO_SHORT = "El nombre debe tener al menos {min} caracteres"
    TOO_LONG = "El nombre no puede exceder {max} caracteres"
    SPECIAL_CHARS = "El nombre '{nombre}' contiene caracteres no permitidos"
    RESERVED = "El nombre '{nombre}' está reservado"
    STARTS_WITH_NUMBER = "El nombre '{nombre}' no puede empezar con números"
    DUPLICATED = "El nombre '{nombre}' ya está en uso"
    ALREADY_USED = "El nombre '{nombre}' ya fue utilizado anteriormente"


class NameEN(NameES):
    LANGUAGE = Language.ENGLISH

    EMPTY = "Username cannot be empty"
    TOO_SHORT = "Name must be at least {min} characters long"
    TOO_LONG = "Name cannot exceed {max} characters"
    SPECIAL_CHARS = "Name '{nombre}' contains invalid characters"
    RESERVED = "Name '{nombre}' is reserved"
    STARTS_WITH_NUMBER = "Name '{nombre}' cannot start with numbers"
    DUPLICATED = "Name '{nombre}' is already in use"
    ALREADY_USED = "Name '{nombre}' was previously used"


ENTITY = "name"
CATALOGS = {Language.SPANISH: NameES, Language.ENGLISH: NameEN}
