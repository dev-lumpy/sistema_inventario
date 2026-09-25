 # tests/infrastructure/password/test_password_hasher_django.py
"""Tests del adapter PasswordHasherDjango.

Este adapter NO toca base de datos. Solo usa funciones de hashing de
Django (make_password, check_password), que son puras y no persistentes.

Por eso NO necesita @pytest.mark.django_db.
"""

import pytest

from infrastructure.django.auth.password_hasher_django import PasswordHasherDjango
from core.domain.usuario.value_objects import Password, PasswordHash


@pytest.fixture
def hasher() -> PasswordHasherDjango:
    return PasswordHasherDjango()


# =========================================================================
# hashear
# =========================================================================

def test_hashear_no_devuelve_la_password_plana(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: el hasher devuelve la contraseña en texto plano.

    Bug de seguridad crítico.
    """
    pwd = Password("Abc123!x")
    hash_ = hasher.hashear(pwd)

    assert hash_ != pwd.valor
    assert "Abc123!x" not in hash_.valor


def test_hashear_devuelve_un_string_no_vacio(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: el hasher devuelve None o string vacío.

    Rompe cuando alguien rompe el adapter.
    """
    hash_ = hasher.hashear(Password("Abc123!x"))

    assert isinstance(hash_, PasswordHash)
    assert len(hash_.valor) > 0


def test_hashear_usa_algoritmo_de_django(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: el hash no tiene el formato de Django.

    Django prefixa el hash con el algoritmo: "pbkdf2_sha256$...", "argon2$...",
    etc. Este test verifica que se está usando el hasher de Django y no
    algo casero como hashlib.md5.
    """
    hash_ = hasher.hashear(Password("Abc123!x"))

    # El formato es: <algoritmo>$<params>$<salt>$<hash>
    assert "$" in hash_.valor
    partes = hash_.valor.split("$")
    assert len(partes) >= 3


def test_hashear_es_no_determinista(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: hashear dos veces la misma contraseña da el mismo hash.

    Eso sería un bug de seguridad: significa que no hay salt aleatorio.
    Django usa salt por defecto, así que dos hashes deben ser distintos.
    """
    pwd = Password("Abc123!x")

    hash_1 = hasher.hashear(pwd)
    hash_2 = hasher.hashear(pwd)

    assert hash_1 != hash_2


# =========================================================================
# verificar
# =========================================================================

def test_verificar_acepta_la_password_correcta(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: verificar rechaza una contraseña correcta.

    Rompe el flujo de login.
    """
    pwd = Password("Abc123!x")
    hash_ = hasher.hashear(pwd)

    assert hasher.verificar(pwd, hash_) is True


def test_verificar_rechaza_una_password_incorrecta(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: verificar acepta cualquier contraseña.

    Bug de seguridad crítico: login sin autenticación real.
    """
    hash_ = hasher.hashear(Password("Abc123!x"))

    assert hasher.verificar(Password("Otra123!x"), hash_) is False


def test_verificar_rechaza_hash_vacio(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: verificar acepta hash vacío.

    Bug: si el hash está vacío en BD, alguien podría entrar con cualquier pass.
    """
    assert hasher.verificar(Password("Abc123!x"), PasswordHash("Otra123!x")) is False


# =========================================================================
# Contrato: hashear + verificar son consistentes entre sí
# =========================================================================

def test_hashear_y_verificar_son_consistentes(hasher: PasswordHasherDjango) -> None:
    """
    Si falla: el hash generado por hashear no es verificable por verificar.

    Este es el contrato más importante del adapter: si hasheás una
    contraseña, verificar con la misma contraseña debe dar True.
    """
    pwd = Password("Abc123!x")
    hash_ = hasher.hashear(pwd)

    assert hasher.verificar(pwd, hash_) is True
    assert hasher.verificar(Password("Otra123!x"), hash_) is False
