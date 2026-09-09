# core/domain/exceptions.py

from typing import Any, Dict, Optional
from core.i18n.manager import MessageManager


class DomainException(Exception):
    """Base para TODOS los errores de dominio"""
    
    def __init__(
        self,
        code: str,
        message: str,
        user_message: Optional[str] = None,
        status_code: int = 400,
        severity: str = "error",
        **context: Any
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.severity = severity
        self.context = context
        
        # Extraer message_key/language del context si vienen de subclases
        message_key = context.pop("message_key", None)
        language = context.pop("language", None)
        
        if message_key:
            self.user_message = MessageManager.get_message(message_key, language or "", **context)
        else:
            self.user_message = user_message or message
        
        for key, value in context.items():
            setattr(self, key, value)
        
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.user_message,
                "severity": self.severity,
                "details": self.context
            }
        }
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
