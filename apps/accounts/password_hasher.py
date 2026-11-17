from __future__ import annotations

from django.contrib.auth.hashers import check_password, make_password

from core.application.ports.password_hasher import PasswordHasher
from core.domain.accounts.value_objects import PasswordHash


class DjangoPasswordHasher(PasswordHasher):
    def hashear(self, password: str) -> PasswordHash:
        return PasswordHash(make_password(password))

    def verificar(self, password: str, password_hash: PasswordHash) -> bool:
        return check_password(password, password_hash.valor)
