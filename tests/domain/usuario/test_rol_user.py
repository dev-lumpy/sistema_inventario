 # tests/domain/usuario/test_rol_user.py
"""Tests del Value Object RolUser."""

import pytest

from core.domain.usuario.exceptions import RolInvalidoException
from core.domain.usuario.value_objects import RolUser


@pytest.mark.parametrize("valor", ["vendedor", "administrador"])
def test_rol_acepta_valores_validos(valor: str) -> None:
    rol = RolUser(valor)
    assert rol.valor == valor


def test_rol_rechaza_valor_no_string() -> None:
    """
    Si falla: RolUser(123) se cuela sin lanzar excepción.

    El isinstance() es la primera línea de defensa.
    """
    with pytest.raises(RolInvalidoException):
        RolUser(123)  # type: ignore[arg-type]


def test_rol_rechaza_vacio() -> None:
    with pytest.raises(RolInvalidoException):
        RolUser("")


def test_rol_rechaza_solo_espacios() -> None:
    """
    Si falla: RolUser("   ") pasa porque no chequea strip.
    """
    with pytest.raises(RolInvalidoException):
        RolUser("   ")


def test_rol_rechaza_valor_desconocido() -> None:
    with pytest.raises(RolInvalidoException):
        RolUser("superadmin")


@pytest.mark.parametrize(
    "valor,invalido",
    [
        ("Vendedor", True),       # capitalizado
        ("VENDEDOR", True),       # mayúsculas
        ("vendedor ", True),      # trailing space
        (" vendedor", True),      # leading space
    ],
)
def test_rol_no_normaliza_case_ni_espacios(valor: str, invalido: bool) -> None:
    """
    Si falla: RolUser("Vendedor") pasa cuando debería fallar.

    El VO es estricto: solo acepta exactamente "vendedor" o
    "administrador" en minúsculas. Cualquier variación debe fallar.
    """
    if invalido:
        with pytest.raises(RolInvalidoException):
            RolUser(valor)


# --- Properties ------------------------------------------------------------

def test_rol_es_vendedor() -> None:
    """
    Si falla: la property es_vendedor devuelve mal.
    """
    assert RolUser("vendedor").es_vendedor is True
    assert RolUser("administrador").es_vendedor is False


def test_rol_es_administrador() -> None:
    assert RolUser("administrador").es_administrador is True
    assert RolUser("vendedor").es_administrador is False
