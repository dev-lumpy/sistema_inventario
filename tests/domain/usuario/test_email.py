 # tests/domain/usuario/test_email.py
"""Tests del Value Object Email."""

import pytest

from core.domain.usuario.exceptions import EmailInvalidoException
from core.domain.usuario.value_objects import Email


# --- Casos válidos ---------------------------------------------------------

@pytest.mark.parametrize(
    "entrada",
    [
        "user@example.com",
        "USER@EXAMPLE.COM",
        "  user@example.com  ",
        "a@b.co",
        "test.tag@sub.dominio.com.ar",
    ],
)
def test_email_acepta_formatos_validos(entrada: str) -> None:
    """
    Si falla: Email rechaza entradas que debería aceptar.
    """
    email = Email(entrada)
    assert email.valor == entrada.strip().lower()


def test_email_normaliza_strip_y_lower() -> None:
    """
    Si falla: Email no normaliza (deja espacios o mayúsculas).

    Esto importa porque dos emails 'iguales' con distinto casing deben
    comparar igual como VOs.
    """
    a = Email("  User@Example.COM  ")
    b = Email("user@example.com")
    assert a == b


# --- Casos inválidos -------------------------------------------------------

@pytest.mark.parametrize(
    "entrada",
    [
        "",
        "   ",
        "sin-arroba.com",
        "sin@dominio",
        "con espacio@dominio.com",
        "@sin-usuario.com",
        "usuario@",
    ],
)
def test_email_rechaza_formatos_invalidos(entrada: str) -> None:
    """
    Si falla: Email acepta algo que no es un email.

    Atrapa cuando alguien relaja la validación.
    """
    with pytest.raises(EmailInvalidoException):
        Email(entrada)
