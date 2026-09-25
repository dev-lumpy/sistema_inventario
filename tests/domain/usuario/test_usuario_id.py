 # tests/domain/usuario/test_usuario_id.py
"""Tests del Value Object UsuarioId."""

from uuid import UUID, uuid4

import pytest

from core.domain.usuario.exceptions import UsuarioIdInvalidoException
from core.domain.usuario.value_objects import UsuarioId


def test_usuario_id_acepta_uuid() -> None:
    uid = uuid4()
    usuario_id = UsuarioId(uid)
    assert usuario_id.valor == uid


def test_usuario_id_acepta_string_uuid_valido() -> None:
    """
    Si falla: UsuarioId no convierte strings UUID a UUID.

    El __post_init__ intenta `UUID(self.valor)` cuando no es un UUID.
    """
    uid = uuid4()
    usuario_id = UsuarioId(str(uid))  # type: ignore[arg-type]
    assert isinstance(usuario_id.valor, UUID)
    assert usuario_id.valor == uid


@pytest.mark.parametrize(
    "entrada",
    ["no-es-uuid", "12345", "", "  ", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
)
def test_usuario_id_rechaza_strings_invalidos(entrada: str) -> None:
    """
    Si falla: UsuarioId acepta basura como UUID.
    """
    with pytest.raises(UsuarioIdInvalidoException):
        UsuarioId(entrada)  # type: ignore[arg-type]


def test_usuario_id_generar_devuelve_uno_nuevo_cada_vez() -> None:
    """
    Si falla: generar() está cacheando el mismo UUID.

    Deben ser distintos: cada llamada genera un UUID v4 nuevo.
    """
    a = UsuarioId.generar()
    b = UsuarioId.generar()
    assert a.valor != b.valor


def test_usuario_id_desde_str() -> None:
    uid = uuid4()
    usuario_id = UsuarioId.desde_str(str(uid))
    assert usuario_id.valor == uid
