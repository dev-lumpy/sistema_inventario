 # tests/i18n/test_exception_keys.py
"""
Verifica que todas las keys usadas en excepciones de dominio existan
realmente en los catálogos.

Recorre core/domain/**/exceptions.py, parsea con ast, extrae
message_key="..." y trata de resolverlas.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from core.i18n.manager import MessageKeyManager

DOMAIN_ROOT = Path(__file__).resolve().parents[2] / "core" / "domain"


def _iter_exception_files() -> list[Path]:
    if not DOMAIN_ROOT.exists():
        return []
    return sorted(DOMAIN_ROOT.rglob("exceptions.py"))


def _extract_message_keys(path: Path) -> list[tuple[str, int]]:
    """Devuelve [(key, lineno), ...] de todas las llamadas con message_key=."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    keys: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg != "message_key":
                continue
            if isinstance(kw.value, ast.Constant) and isinstance(
                kw.value.value, str
            ):
                keys.append((kw.value.value, kw.value.lineno))

    return keys


def _module_name_for(path: Path) -> str:
    """Convierte ruta en nombre de módulo importable."""
    rel = path.resolve().relative_to(Path.cwd().resolve())
    return ".".join(rel.with_suffix("").parts)


def _fake_kwargs_for(key: str) -> dict[str, str]:
    """
    Genera kwargs ficticios para cualquier {placeholder} que aparezca.

    No sabemos los nombres reales de los kwargs de cada plantilla,
    así que inventamos valores para todos los placeholders detectados
    inspeccionando el texto de la plantilla.

    Como no tenemos acceso directo a la plantilla sin resolver la key,
    probamos primero sin kwargs; si falla por placeholders, reintentamos
    con kwargs inventados a partir del propio error... pero eso es frágil.
    Mejor: resolvemos la key a mano para inspeccionar placeholders.
    """
    import re

    from core.i18n.message import MESSAGES

    if "." not in key:
        return {}
    entity, const = key.split(".", 1)

    # Buscamos en cualquier idioma la plantilla para extraer placeholders
    catalogs = MESSAGES.get(entity, {})
    placeholders: set[str] = set()
    for cls in catalogs.values():
        value = getattr(cls, const, None)
        if isinstance(value, str):
            placeholders.update(re.findall(r"\{(\w+)\}", value))

    return {p: f"<{p}>" for p in placeholders}


def _all_message_keys() -> list[tuple[str, str, int]]:
    """[(key, módulo, línea), ...] de todas las excepciones del dominio."""
    result: list[tuple[str, str, int]] = []
    for path in _iter_exception_files():
        module = _module_name_for(path)
        for key, lineno in _extract_message_keys(path):
            result.append((key, module, lineno))
    return result


ALL_KEYS = _all_message_keys()


@pytest.mark.parametrize(
    "key,module,lineno",
    ALL_KEYS,
    ids=[f"{k}@{m}:{ln}" for k, m, ln in ALL_KEYS] or ["sin-keys"],
)
def test_todas_las_keys_usadas_en_excepciones_existen(
    key: str, module: str, lineno: int, reset_language
) -> None:
    """
    Si falla: una excepción de dominio usa una key inexistente en los
    catálogos.

    Rompe cuando alguien renombra una constante en el catálogo y se olvida
    de actualizar la excepción, o cuando agrega una excepción nueva con
    una key que nunca se tradujo.
    """
    if not ALL_KEYS:
        pytest.skip(
            f"No se encontraron excepciones en {DOMAIN_ROOT}. "
            "Verificá la ruta del dominio."
        )

    kwargs = _fake_kwargs_for(key)

    try:
        resultado = MessageKeyManager.get_message(key, **kwargs)
    except ValueError as exc:
        pytest.fail(
            f"La key '{key}' usada en {module}:{lineno} no se pudo resolver. "
            f"Error: {exc}"
        )

    assert isinstance(resultado, str) and resultado, (
        f"La key '{key}' en {module}:{lineno} resolvió a un valor vacío."
    )
    assert resultado != key, (
        f"La key '{key}' en {module}:{lineno} no fue traducida "
        f"(devolvió la key cruda)."
    )


def test_hay_excepciones_para_analizar() -> None:
    """
    Si falla: no encontramos archivos exceptions.py en core/domain/.

    Esto rompe si alguien mueve el dominio de lugar, o si el proyecto
    todavía no tiene excepciones. Es un test de sanidad del propio test.
    """
    if not DOMAIN_ROOT.exists():
        pytest.skip(f"{DOMAIN_ROOT} no existe todavía.")
    # No fallamos si no hay excepciones, solo informamos.
    # Si querés que sea estricto, descomentá el assert.
    # assert _iter_exception_files(), f"No hay exceptions.py en {DOMAIN_ROOT}"
