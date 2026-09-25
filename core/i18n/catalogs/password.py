 # core/i18n/catalogs/password.py
from .base import Language, MessageKey


class PasswordES(MessageKey):
    LANGUAGE = Language.SPANISH

    NOT_STRING = "La contraseña debe ser una cadena de texto"
    EMPTY = "La contraseña no puede estar vacía"
    WHITESPACE_EDGES = "La contraseña no puede empezar ni terminar con espacios"
    TOO_SHORT = "La contraseña debe tener al menos {min} caracteres"
    TOO_LONG = "La contraseña no puede superar los {max} caracteres"
    NO_UPPERCASE = "La contraseña debe contener al menos una mayúscula"
    NO_LOWERCASE = "La contraseña debe contener al menos una minúscula"
    NO_DIGIT = "La contraseña debe contener al menos un número"
    NO_SPECIAL = "La contraseña debe contener al menos un carácter especial"
    HAS_SPACES = "La contraseña no puede contener espacios"
    TOO_PREDICTABLE = "La contraseña es demasiado predecible"

    # Para el Hash
    HASH_EMPTY = "El hash de contraseña no puede estar vacío"


class PasswordEN(PasswordES):
    LANGUAGE = Language.ENGLISH

    NOT_STRING = "Password must be a string"
    EMPTY = "Password cannot be empty"
    WHITESPACE_EDGES = "Password cannot start or end with whitespace"
    TOO_SHORT = "Password must be at least {min} characters long"
    TOO_LONG = "Password cannot exceed {max} characters"
    NO_UPPERCASE = "Password must contain at least one uppercase letter"
    NO_LOWERCASE = "Password must contain at least one lowercase letter"
    NO_DIGIT = "Password must contain at least one digit"
    NO_SPECIAL = "Password must contain at least one special character"
    HAS_SPACES = "Password cannot contain spaces"
    TOO_PREDICTABLE = "Password is too predictable"
    HASH_EMPTY = "Password hash cannot be empty"


ENTITY = "password"
CATALOGS = {Language.SPANISH: PasswordES, Language.ENGLISH: PasswordEN}
