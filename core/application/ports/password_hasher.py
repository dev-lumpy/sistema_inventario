# core/application/ports/password_hasher.py
"""Puerto para el servicio de hasheo de contraseñas"""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hashear(self, password: str) -> str:
        ...

    @abstractmethod
    def verificar(self, password: str, hash: str) -> bool:
        ...