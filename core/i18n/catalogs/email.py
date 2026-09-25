# core/i18n/catalogs/email.py
from .base import Language, MessageKey


class EmailES(MessageKey):
    LANGUAGE = Language.SPANISH

    NOT_STRING = "El email debe ser una cadena de texto"
    EMPTY = "El email no puede estar vacío"
    TOO_LONG = "El email no puede superar los {max} caracteres"
    INVALID_FORMAT = "El email '{email}' no tiene un formato válido"
    INVALID_LOCAL_PART = "El email '{email}' tiene puntos consecutivos o al inicio/fin"
    ALREADY_EXISTS = "El email '{email}' ya está registrado"


class EmailEN(EmailES):
    LANGUAGE = Language.ENGLISH

    NOT_STRING = "Email must be a string"
    EMPTY = "Email cannot be empty"
    TOO_LONG = "Email cannot exceed {max} characters"
    INVALID_FORMAT = "Email '{email}' does not have a valid format"
    INVALID_LOCAL_PART = "Email '{email}' has consecutive dots or starts/ends with a dot"
    ALREADY_EXISTS = "Email '{email}' already registered"


ENTITY = "email"
CATALOGS = {Language.SPANISH: EmailES, Language.ENGLISH: EmailEN}
