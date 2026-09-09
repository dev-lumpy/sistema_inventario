 # core/i18n/manager.py
"""Gestor de internacionalización"""

from typing import Dict, Any, Optional
from .message import MESSAGES, Language


class MessageManager:
    """Gestor de mensajes multilenguaje"""
    
    _default_language = Language.SPANISH
    
    @classmethod
    def get_message(cls, key: str, language: str = "", **kwargs) -> str:
        language = language or cls._default_language
        
        # Obtener mensaje
        message_template = MESSAGES.get(language, {}).get(key)
        
        # Si no existe el mensaje, EXPLOTA (es un bug del dev)
        if not message_template:
            raise ValueError(f"Message key '{key}' not found for language '{language}'")
        
        # Si no se pasaron todas las variables, EXPLOTA (es un bug del dev)
        return message_template.format(**kwargs)
    
    @classmethod
    def set_default_language(cls, language: str):
        """Cambiar el idioma por defecto"""
        if language in MESSAGES:
            cls._default_language = language

