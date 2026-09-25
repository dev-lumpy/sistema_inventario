# core/i18n/catalogs/base.py
from typing import ClassVar


class Language:
    SPANISH = "es"
    ENGLISH = "en"
    # Agregar idiomas aquí. Cada catálogo debe tener una clase por idioma.


class MessageKey:
    """
    Clase base de un catálogo por entidad.

    - Cada constante de clase es una key.
    - Cada subclase representa un idioma.
    - La subclase del idioma primario hereda a las demás para fallback.
    """
    LANGUAGE: ClassVar[str] = "en"

    @classmethod
    def get(cls, key: str) -> str | None:
        return getattr(cls, key, None)
