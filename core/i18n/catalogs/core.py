from .base import Language, MessageKey


class CoreES(MessageKey):
    LANGUAGE = Language.SPANISH
    PERMISSION_DENIED = "Permiso denegado"


class CoreEN(MessageKey):
    LANGUAGE = Language.ENGLISH
    PERMISSION_DENIED = "Permission denied"


ENTITY = "core"
CATALOGS = {
    Language.SPANISH: CoreES,
    Language.ENGLISH: CoreEN,
}
