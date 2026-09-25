 # core/i18n/catalogs/role.py
from .base import Language, MessageKey


class RoleES(MessageKey):
    LANGUAGE = Language.SPANISH

    NOT_STRING = "El rol debe ser una cadena de texto"
    EMPTY = "El rol no puede estar vacío"
    INVALID = "Rol inválido: '{valor}'. Valores permitidos: {valores_validos}"


class RoleEN(RoleES):
    LANGUAGE = Language.ENGLISH

    NOT_STRING = "Role must be a string"
    EMPTY = "Role cannot be empty"
    INVALID = "Invalid role: '{valor}'. Allowed values: {valores_validos}"


ENTITY = "role"
CATALOGS = {Language.SPANISH: RoleES, Language.ENGLISH: RoleEN}
