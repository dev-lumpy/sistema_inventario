# core/application/ports/password_hasher.py
"""Puerto para el servicio de hasheo de contraseñas"""

from abc import ABC, abstractmethod

from core.domain.usuario.value_objects import Password, PasswordHash


class PasswordHasher(ABC):
    @abstractmethod
    def hashear(self, password: Password) -> PasswordHash:
        ...

    @abstractmethod
    def verificar(self, password: Password, hash: PasswordHash) -> bool:
        ...
