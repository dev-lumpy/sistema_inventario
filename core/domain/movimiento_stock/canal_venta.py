"""Enum CanalVenta para MovimientoStock"""

from enum import Enum


class CanalVenta(Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    PRESENCIAL = "presencial"
    OTRO = "otro"