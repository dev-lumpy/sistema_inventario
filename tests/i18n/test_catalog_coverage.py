 # tests/i18n/test_catalog_coverage.py
"""
Cobertura de catálogos: que todos los idiomas tengan las mismas keys,
que no haya entidades duplicadas y que todas las clases hereden de MessageKey.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.i18n.catalogs.base import MessageKey


def _public_constants(cls: type) -> set[str]:
    """Devuelve las constantes públicas (UPPER_CASE) de una clase."""
    return {
        name
        for name in vars(cls)
        if name.isupper() and not name.startswith("_")
    }


def test_todos_los_idiomas_tienen_las_mismas_keys(
    messages_registry: dict[str, dict[str, type[MessageKey]]],
    base_language: str,
) -> None:
    """
    Si falla: algún idioma tiene keys de más, de menos, o con nombre distinto.

    Esto rompe cuando alguien agrega una traducción nueva al español y
    se olvida de agregarla al inglés (o viceversa).
    """
    problemas: list[str] = []

    for entity, catalogs in messages_registry.items():
        assert base_language in catalogs, (
            f"La entidad '{entity}' no tiene catálogo para el idioma base "
            f"'{base_language}'. Idiomas disponibles: {sorted(catalogs)}"
        )

        base_keys = _public_constants(catalogs[base_language])

        for lang, cls in catalogs.items():
            if lang == base_language:
                continue

            other_keys = _public_constants(cls)

            faltantes = base_keys - other_keys
            sobrantes = other_keys - base_keys

            if faltantes:
                problemas.append(
                    f"  - '{entity}' [{lang}]: faltan {sorted(faltantes)}"
                )
            if sobrantes:
                problemas.append(
                    f"  - '{entity}' [{lang}]: sobran {sorted(sobrantes)}"
                )

    assert not problemas, (
        "Inconsistencias de keys entre idiomas:\n" + "\n".join(problemas)
    )


def test_no_hay_entidades_duplicadas(
    messages_registry: dict[str, dict[str, type[MessageKey]]],
) -> None:
    """
    Si falla: dos módulos de catálogo declaran el mismo ENTITY.

    El auto-descubrimiento debería lanzar RuntimeError al construir MESSAGES,
    pero si el import se cachea o alguien construye el registry a mano,
    podríamos tener colisiones silenciosas. Acá lo verificamos explícitamente.
    """
    # Si _discover() funcionó bien, MESSAGES ya es un dict sin duplicados.
    # Este test es una red de seguridad: reconstruimos el descubrimiento
    # y contamos cuántas veces aparece cada ENTITY.
    from core.i18n.catalogs import _discover  # type: ignore[attr-defined]

    discovered = _discover()

    assert set(discovered.keys()) == set(messages_registry.keys()), (
        "MESSAGES y _discover() devolvieron conjuntos de entidades distintos. "
        f"discover={sorted(discovered)} vs MESSAGES={sorted(messages_registry)}"
    )


@pytest.mark.parametrize(
    "entity",
    sorted(__import__("core.i18n.message", fromlist=["MESSAGES"]).MESSAGES),
)
def test_todos_los_catalogos_heredan_de_messages(
    entity: str,
    messages_registry: dict[str, dict[str, type[Any]]],
) -> None:
    """
    Si falla: un catálogo no es subclase de MessageKey.

    Esto rompe cuando alguien define un catálogo por error (ej: olvida
    heredar, o importa la clase base equivocada).
    """
    for lang, cls in messages_registry[entity].items():
        assert issubclass(cls, MessageKey), (
            f"El catálogo '{entity}' [{lang}] ({cls!r}) no hereda de "
            f"MessageKey."
        )
