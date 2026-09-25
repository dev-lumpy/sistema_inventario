 # core/i18n/catalogs/__init__.py
"""
Auto-descubre todos los módulos de este paquete y construye
el registro ENTITY -> {lang: clase}.

Agregar un catálogo = crear un archivo .py acá. Nada más.
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type

from .base import Language, MessageKey


def _discover() -> Dict[str, Dict[str, Type[MessageKey]]]:
    registry: Dict[str, Dict[str, Type[MessageKey]]] = {}
    package_dir = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(package_dir)]):
        name = module_info.name
        if name in ("base", "__init__"):
            continue

        module = importlib.import_module(f"{__name__}.{name}")

        entity = getattr(module, "ENTITY", None)
        catalogs = getattr(module, "CATALOGS", None)

        if entity is None or catalogs is None:
            continue

        if entity in registry:
            raise RuntimeError(
                f"Entity '{entity}' is registered twice "
                f"(check {module.__name__})"
            )

        registry[entity] = catalogs

    return registry


MESSAGES: Dict[str, Dict[str, Type[MessageKey]]] = _discover()
