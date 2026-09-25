 # tests/domain/usuario/test_nombre_usuario.py
"""Tests del Value Object NombreUsuario."""

import pytest

from core.domain.usuario.exceptions import NombreUsuarioInvalidoException
from core.domain.usuario.value_objects import NombreUsuario


def test_nombre_usuario_acepta_valor_valido() -> None:
    nombre = NombreUsuario("Juan")
    assert nombre.valor == "Juan"


def test_nombre_usuario_rechaza_vacio() -> None:
    """
    Si falla: NombreUsuario acepta "" o "   ".
    """
    with pytest.raises(NombreUsuarioInvalidoException):
        NombreUsuario("")


def test_nombre_usuario_rechaza_solo_espacios() -> None:
    """
    Si falla: se cuela un nombre que es puro whitespace.

    Este es un caso que el `if not valor` no atrapa — necesitás
    chequear `.strip() == ""`.
    """
    with pytest.raises(NombreUsuarioInvalidoException):
        NombreUsuario("     ")


def test_nombre_usuario_rechaza_demasiado_corto() -> None:
    with pytest.raises(NombreUsuarioInvalidoException):
        NombreUsuario("J")


def test_nombre_usuario_acepta_longitud_minima() -> None:
    """
    Si falla: el borde exacto del mínimo está mal calculado (off-by-one).

    Con MIN_LENGTH=2, "Jo" debe ser aceptado.
    """
    nombre = NombreUsuario("Jo")
    assert nombre.valor == "Jo"


def test_nombre_usuario_acepta_longitud_maxima() -> None:
    """
    Si falla: el borde exacto del máximo está mal calculado (off-by-one).

    Con MAX_LENGTH=100, exactamente 100 caracteres debe ser válido.
    """
    nombre = NombreUsuario("A" * 100)
    assert len(nombre.valor) == 100


def test_nombre_usuario_rechaza_uno_mas_del_maximo() -> None:
    """
    Si falla: el límite superior está off-by-one.
    """
    with pytest.raises(NombreUsuarioInvalidoException):
        NombreUsuario("A" * 101)
