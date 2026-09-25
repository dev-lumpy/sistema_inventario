 # tests/i18n/test_manager.py
"""
Tests del MessageKeyManager: traducción, cambio de idioma en runtime,
validación de keys y manejo de errores.
"""

from __future__ import annotations

import pytest

from core.i18n.manager import MessageKeyManager
from core.i18n.message import Language


# ---------------------------------------------------------------------------
# Casos felices
# ---------------------------------------------------------------------------

def test_manager_devuelve_mensaje_traducido(reset_language) -> None:
    """
    Si falla: get_message no formatea correctamente el mensaje con kwargs.

    Esperamos que el resultado contenga el valor del parámetro y NO la key
    cruda. Esto rompe cuando alguien cambia el formato de las keys o la
    forma de formatear.
    """
    resultado = MessageKeyManager.get_message(
        "user.NOT_FOUND", usuario_id="u-1"
    )

    assert "u-1" in resultado, (
        f"El mensaje no contiene el valor del parámetro 'usuario_id'. "
        f"Resultado: {resultado!r}"
    )
    assert "user.NOT_FOUND" not in resultado, (
        f"El mensaje contiene la key cruda en vez de la traducción. "
        f"Resultado: {resultado!r}"
    )


def test_manager_cambia_idioma_en_runtime(reset_language) -> None:
    """
    Si falla: set_default_language no tiene efecto en get_message.

    Rompe cuando alguien cachea el catálogo al importar el manager, o
    ignora el idioma por defecto al resolver.
    """
    MessageKeyManager.set_default_language(Language.SPANISH)
    en_es = MessageKeyManager.get_message("user.NOT_FOUND", usuario_id="u-1")

    MessageKeyManager.set_default_language(Language.ENGLISH)
    en_en = MessageKeyManager.get_message("user.NOT_FOUND", usuario_id="u-1")

    assert en_es != en_en, (
        "El mensaje no cambió al cambiar el idioma por defecto. "
        f"es={en_es!r}, en={en_en!r}"
    )
    # El valor del parámetro debe seguir presente en ambos idiomas
    assert "u-1" in en_es
    assert "u-1" in en_en


# ---------------------------------------------------------------------------
# Validación de keys
# ---------------------------------------------------------------------------

def test_manager_falla_si_key_no_tiene_punto(reset_language) -> None:
    """
    Si falla: el manager acepta keys mal formadas sin separador de entidad.

    Rompe cuando alguien relaja la validación de formato de key.
    """
    with pytest.raises(ValueError):
        MessageKeyManager.get_message("userNOTFOUND")


def test_manager_falla_si_entidad_no_existe(reset_language) -> None:
    """
    Si falla: el manager acepta entidades que no están en MESSAGES.

    Rompe cuando alguien hace .get() silencioso o ignora el registry.
    """
    with pytest.raises(ValueError, match="[Uu]nk?nown|entidad|entity"):
        MessageKeyManager.get_message("inventada.X")


def test_manager_falla_si_constante_no_existe(reset_language) -> None:
    """
    Si falla: el manager acepta constantes inexistentes dentro de una
    entidad válida.

    Rompe cuando alguien atrapa AttributeError / devuelve None en vez de
    lanzar ValueError.
    """
    with pytest.raises(ValueError):
        MessageKeyManager.get_message("user.INVENTADA")


def test_manager_falla_si_faltan_placeholders(reset_language) -> None:
    """
    Si falla: el manager no valida que los placeholders de la plantilla
    coincidan con los kwargs.

    Rompe cuando alguien hace str.format() sin try/except o atrapa
    KeyError silenciosamente.
    """
    # No pasamos usuario_id aunque la plantilla lo requiere
    with pytest.raises(ValueError):
        MessageKeyManager.get_message("user.NOT_FOUND")

