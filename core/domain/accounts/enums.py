from __future__ import annotations

from enum import Enum


class Rol(str, Enum):
    ADMINISTRADOR = "administrador"
    VENDEDOR = "vendedor"


class EstadoVinculo(str, Enum):
    PENDIENTE = "pendiente"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado"
    INACTIVO = "inactivo"


class SolicitadoPor(str, Enum):
    ADMIN = "admin"
    VENDEDOR = "vendedor"
