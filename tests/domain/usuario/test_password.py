 # tests/domain/usuario/test_password.py
"""Tests del Value Object Password.

Password tiene 11 reglas de validación. Cada una se testea individualmente
para que, si alguna se rompe, sepamos exactamente cuál.
"""

import pytest

from core.domain.usuario.exceptions import PasswordInvalidaException
from core.domain.usuario.value_objects import Password


# =========================================================================
# Caso feliz
# =========================================================================

def test_password_acepta_password_valida() -> None:
    """
    Si falla: la validación es demasiado estricta y rechaza passwords
    que cumplen todas las reglas.
    """
    pwd = Password("Abc123!x")
    assert pwd.valor == "Abc123!x"


# =========================================================================
# Reglas de tipo y vacío
# =========================================================================

def test_password_rechaza_no_string() -> None:
    """Si falla: acepta 12345 (int) como password."""
    with pytest.raises(PasswordInvalidaException):
        Password(12345)  # type: ignore[arg-type]


def test_password_rechaza_vacio() -> None:
    with pytest.raises(PasswordInvalidaException):
        Password("")


def test_password_rechaza_solo_espacios() -> None:
    """
    Si falla: Password("        ") (8 espacios) pasa si no chequeás strip.
    """
    with pytest.raises(PasswordInvalidaException):
        Password("        ")


def test_password_rechaza_espacios_en_los_bordes() -> None:
    """
    Si falla: Password(" Abc123!x ") pasa, pero tiene espacios al borde.

    Es un caso real: usuarios que copian/pegan con espacios accidentales.
    """
    with pytest.raises(PasswordInvalidaException):
        Password(" Abc123!x ")


# =========================================================================
# Reglas de longitud
# =========================================================================

def test_password_rechaza_demasiado_corta() -> None:
    with pytest.raises(PasswordInvalidaException):
        Password("Ab1!xyz")  # 7 caracteres, mínimo 8


def test_password_acepta_longitud_minima_exacta() -> None:
    """
    Si falla: off-by-one en LONGITUD_MINIMA.

    "Abc123!x" tiene exactamente 8 caracteres → debe pasar.
    """
    pwd = Password("Abc123!x")
    assert len(pwd.valor) == 8


def test_password_acepta_longitud_maxima_exacta() -> None:
    """
    Si falla: off-by-one en LONGITUD_MAXIMA.

    Construimos una password de exactamente 128 caracteres que cumpla
    todas las reglas, incluyendo la de no tener 4+ repetidos ni secuencias.
    """
    # Generamos un relleno sin 4 repetidos ni secuencias.
    # Patrón: repetimos una base corta que no sea secuencial.
    base = "Qx9z"          # 4 caracteres únicos, no consecutivos, sin repetidos
    relleno = (base * 31)[:124]   # 124 caracteres sin violar reglas
    pwd_str = f"Ab1!{relleno}"    # 4 + 124 = 128

    assert len(pwd_str) == 128

    pwd = Password(pwd_str)
    assert len(pwd.valor) == 128


def test_password_rechaza_uno_mas_del_maximo() -> None:
    relleno = "a" * 125
    pwd_str = f"Ab1!{relleno}"  # 4 + 125 = 129
    with pytest.raises(PasswordInvalidaException):
        Password(pwd_str)


# =========================================================================
# Reglas de composición
# =========================================================================

def test_password_rechaza_sin_mayuscula() -> None:
    """
    Si falla: "abc123!x" (sin mayúscula) pasa.
    """
    with pytest.raises(PasswordInvalidaException):
        Password("abc123!x")


def test_password_rechaza_sin_minuscula() -> None:
    with pytest.raises(PasswordInvalidaException):
        Password("ABC123!X")


def test_password_rechaza_sin_digito() -> None:
    with pytest.raises(PasswordInvalidaException):
        Password("Abcdef!x")


def test_password_rechaza_sin_especial() -> None:
    """
    Si falla: "Abc12345" (sin especial) pasa.
    """
    with pytest.raises(PasswordInvalidaException):
        Password("Abc12345")


def test_password_rechaza_con_espacios_internos() -> None:
    """
    Si falla: "Abc 123!x" (con espacio en el medio) pasa.

    El espacio es un carácter válido en algunos sistemas, pero acá se
    prohíbe explícitamente.
    """
    with pytest.raises(PasswordInvalidaException):
        Password("Abc 123!x")


# =========================================================================
# Regla de predictibilidad: repetidos
# =========================================================================

@pytest.mark.parametrize(
    "password",
    [
        "Abc1111!",    # 4 unos seguidos
        "Abcaaaa1!",   # 4 aes seguidas
        "ABCAAAAz1!",  # 4 A seguidas, y 'z' para cumplir minúscula
    ],
)
def test_password_rechaza_caracteres_repetidos(password: str) -> None:
    """
    Si falla: passwords con 4+ caracteres iguales seguidos pasan.

    Atrapa cuando alguien rompe la regex `(.)\\1{3,}`.
    """
    with pytest.raises(PasswordInvalidaException):
        Password(password)


def test_password_acepta_tres_repetidos() -> None:
    """
    Si falla: el umbral de repetidos está mal.
    Con 4+ repetidos debe fallar, con 3 debe pasar.

    Usamos 'Qxaaa9!z': tiene 3 'a' seguidas, mayúscula, dígito, especial,
    sin secuencias alfabéticas ni numéricas, sin espacios.
    """
    pwd = Password("Qxaaa9!z")
    assert pwd.valor == "Qxaaa9!z"
