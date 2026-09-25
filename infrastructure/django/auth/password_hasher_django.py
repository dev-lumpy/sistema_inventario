# core/adapters/password_hasher_django.py
"""Adapter para elegir el Hash"""

from django.contrib.auth.hashers import check_password, make_password

from core.application.ports.password_hasher import PasswordHasher
from core.domain.usuario.value_objects import Password, PasswordHash


class PasswordHasherDjango(PasswordHasher):

    def hashear(self, password: Password) -> PasswordHash:
        return PasswordHash(make_password(password.valor))
        
    def verificar(self, password: Password, hash: PasswordHash) -> bool:
        return check_password(password.valor, hash.valor)
