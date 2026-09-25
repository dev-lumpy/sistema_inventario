 # core/i18n/catalogs/admin.py
from .base import Language, MessageKey


class AdminES(MessageKey):
    LANGUAGE = Language.SPANISH

    NOT_FOUND = "Administrador no encontrado: {usuario_id}"
    NOT_ADMIN = "El usuario '{usuario_id}' no tiene rol de administrador"


class AdminEN(AdminES):
    LANGUAGE = Language.ENGLISH

    NOT_FOUND = "Administrator not found: {usuario_id}"
    NOT_ADMIN = "User '{usuario_id}' does not have administrator role"


ENTITY = "admin"
CATALOGS = {Language.SPANISH: AdminES, Language.ENGLISH: AdminEN}
