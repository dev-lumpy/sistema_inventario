# core/i18n/message.py

"""Catálogo de mensajes multilenguaje (auto-descubierto)"""

from core.i18n.catalogs import MESSAGES
from core.i18n.catalogs.base import Language, MessageKey

# Re-export para no romper imports existentes
__all__ = ["Language", "MessageKey", "MESSAGES"]
