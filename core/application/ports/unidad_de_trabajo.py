# core/application/ports/unidad_de_trabajo.py
"""Puerto para Unit of Work (transacciones)"""

from __future__ import annotations

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> UnitOfWork:
        ...

    @abstractmethod
    def __exit__(self, *args) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...