"""Módulo compartido del dominio - VOs y excepciones base"""

from core.domain.shared.exceptions import DomainException
from core.domain.shared.fecha import Fecha
from core.domain.shared.id import Id

__all__ = [
    'DomainException',
    'Fecha',
    'Id',
]