 # tests/i18n/conftest.py
"""
Fixtures compartidos para los tests del sistema i18n.

Solo aplica a los tests dentro de tests/i18n/.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.i18n.manager import MessageKeyManager
from core.i18n.message import MESSAGES, Language, MessageKey


@pytest.fixture
def reset_language() -> Any:
    """
    Aísla el estado global de MessageKeyManager entre tests.

    Guarda el idioma por defecto antes del test y lo restaura al terminar,
    incluso si el test falla. Evita que un test que cambia el idioma
    contamine a los siguientes.
    """
    original = getattr(
        MessageKeyManager,
        "default_language",
        getattr(MessageKeyManager, "default_language", None),
    )

    yield

    if original is not None:
        try:
            MessageKeyManager.setdefault_language(original)
        except Exception:
            # Fallback por si el setter no existe o falla
            if hasattr(MessageKeyManager, "default_language"):
                MessageKeyManager.default_language = original
            elif hasattr(MessageKeyManager, "default_language"):
                MessageKeyManager.default_language = original


@pytest.fixture
def messages_registry() -> dict[str, dict[str, type[MessageKey]]]:
    """Expone el registro MESSAGES (entidad -> idioma -> clase)."""
    return MESSAGES


@pytest.fixture
def language() -> type[Language]:
    """Expone la clase Language (con SPANISH, ENGLISH, etc.)."""
    return Language


@pytest.fixture
def base_language() -> str:
    """
    Idioma base para comparaciones de cobertura.

    Convención: el idioma primario es el que declara MessageKey.LANGUAGE
    (por defecto "en"). Si cambia, se ajusta en un solo lugar.
    """
    return MessageKey.LANGUAGE
