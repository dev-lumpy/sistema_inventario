# core/i18n/catalogs/auth.py
from .base import Language, MessageKey


class AuthES(MessageKey):
    LANGUAGE = Language.SPANISH

    INVALID_CREDENTIALS = "Credenciales inválidas"
    NOT_AUTHENTICATED = "No estás autenticado"
    PERMISSION_DENIED = "No tienes permiso para realizar esta acción"
    TOKEN_INVALID = "El token es inválido o ha expirado"
    TOKEN_EXPIRED = "El token ha expirado"


class AuthEN(AuthES):
    LANGUAGE = Language.ENGLISH

    INVALID_CREDENTIALS = "Invalid credentials"
    NOT_AUTHENTICATED = "You are not authenticated"
    PERMISSION_DENIED = "You do not have permission to perform this action"
    TOKEN_INVALID = "Token is invalid or has expired"
    TOKEN_EXPIRED = "Token has expired"


ENTITY = "auth"
CATALOGS = {Language.SPANISH: AuthES, Language.ENGLISH: AuthEN}
