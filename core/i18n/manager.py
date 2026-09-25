# core/i18n/manager.py
from .message import MESSAGES, Language, MessageKey


class MessageKeyManager:
    """Gestor de mensajes multilenguaje"""

    default_language = Language.SPANISH

    @classmethod
    def get_message(cls, key: str, language: str = "", **kwargs) -> str:
        language = language or cls.default_language

        # key con formato: "entidad.CONSTANTE"
        entity, _, const_name = key.partition(".")
        if not const_name:
            raise ValueError(f"Key '{key}' must be '<entity>.<CONSTANT>'")

        catalogs = MESSAGES.get(entity)
        if not catalogs:
            raise ValueError(f"Unknown entity '{entity}' in key '{key}'")

        catalog_cls: MessageKey | None = catalogs.get(language) or catalogs.get(Language.ENGLISH) # pyright: ignore[reportAssignmentType]
        if catalog_cls is None:
            raise ValueError(f"No catalog for entity '{entity}' in language '{language}'")

        template = catalog_cls.get(const_name)
        if template is None:
            raise ValueError(f"MessageKey '{const_name}' not found in entity '{entity}'")

        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Missing placeholder {e} for key '{key}'. Got: {list(kwargs)}"
            ) from e

    @classmethod
    def set_default_language(cls, language: str) -> None:
        if any(language in catalogs for catalogs in MESSAGES.values()):
            cls.default_language = language
