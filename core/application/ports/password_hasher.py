from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.accounts.value_objects import PasswordHash


class PasswordHasher(ABC):
    @abstractmethod
    def hashear(self, password: str) -> PasswordHash:
        ...

    @abstractmethod
    def verificar(self, password: str, password_hash: PasswordHash) -> bool:
        ...
