# core/adapters/password_hasher_django.py
"""Adapter para elegir el Hash"""

from django.contrib.auth.hashers import check_password, make_password

from core.application.ports.password_hasher import PasswordHasher


class PasswordHasherDjango(PasswordHasher):

    def hashear(self, password: str) -> str:
        return make_password(password)
        
    def verificar(self, password: str, hash: str) -> bool:
        return check_password(password, hash)
