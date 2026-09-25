 # tests/i18n/test_placeholders.py
"""
Consistencia de placeholders {var} entre idiomas.

Si un idioma usa {usuario_id} y otro {user_id}, el formateo falla
en runtime para uno de los dos. Este test lo detecta en CI.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from core.i18n.catalogs.base import MessageKey

PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


def _placeholders(value: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(value))


def _public_constants(cls: type) -> dict[str, str]:
    return {
        name: value
        for name, value in vars(cls).items()
        if name.isupper() and not name.startswith("_")
        and isinstance(value, str)
    }


def _iter_comparaciones(
    messages_registry: dict[str, dict[str, type[MessageKey]]],
    base_language: str,
):
    for entity, catalogs in messages_registry.items():
        if base_language not in catalogs:
            continue
        base_values = _public_constants(catalogs[base_language])

        for lang, cls in catalogs.items():
            if lang == base_language:
                continue
            other_values = _public_constants(cls)
            for const, base_text in base_values.items():
                if const not in other_values:
                    continue  # lo cubre test_catalog_coverage
                yield (
                    entity,
                    lang,
                    const,
                    _placeholders(base_text),
                    _placeholders(other_values[const]),
                )


def test_placeholders_consistentes_entre_idiomas(
    messages_registry: dict[str, dict[str, type[MessageKey]]],
    base_language: str,
) -> None:
    """
    Si falla: un idioma tiene placeholders distintos al idioma base.

    Rompe cuando alguien traduce una plantilla y se olvida de un {var},
    lo renombra, o agrega uno nuevo solo en un idioma.
    """
    problemas: list[str] = []

    for entity, lang, const, base_ph, other_ph in _iter_comparaciones(
        messages_registry, base_language
    ):
        if base_ph != other_ph:
            problemas.append(
                f"  - '{entity}.{const}' [{lang}]: "
                f"base={sorted(base_ph)} vs {lang}={sorted(other_ph)}"
            )

    assert not problemas, (
        "Placeholders inconsistentes entre idiomas:\n" + "\n".join(problemas)
    )
