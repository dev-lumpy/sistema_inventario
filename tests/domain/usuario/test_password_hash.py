 # tests/domain/usuario/test_password_hash.py
"""Tests del Value Object PasswordHash.

PasswordHash tiene una sola regla. Solo testeamos el borde y el caso
normal. No merece más.
"""

import pytest

from core.domain.usuario.exceptions import PasswordHashInvalidoException
from core.domain.usuario.value_objects import PasswordHash


def test_password_hash_acepta_hash_no_vacio() -> None:
    ph = PasswordHash("$2b$12$abcdef...")
    assert ph.valor == "$2b$12$abcdef..."


@pytest.mark.parametrize("entrada", ["", "   "])
def test_password_hash_rechaza_vacio(entrada: str) -> None:
    with pytest.raises(PasswordHashInvalidoException):
        PasswordHash(entrada)
