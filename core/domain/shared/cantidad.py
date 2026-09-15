"""Value Object Cantidad - compartido entre Producto y MovimientoStock"""

from __future__ import annotations
from dataclasses import dataclass


class CantidadInvalidaError(ValueError):
    pass


class StockInsuficienteError(ValueError):
    def __init__(self, disponible: int, solicitado: int):
        self.disponible = disponible
        self.solicitado = solicitado
        super().__init__(f"Stock insuficiente. Disponible: {disponible}, Solicitado: {solicitado}")


@dataclass(frozen=True)
class Cantidad:
    """Value Object que representa una cantidad entera no negativa"""
    valor: int

    def __post_init__(self):
        if self.valor < 0:
            raise CantidadInvalidaError(f"Cantidad inválida (negativa): {self.valor}")

    def sumar(self, cantidad: int) -> Cantidad:
        if cantidad < 0:
            raise CantidadInvalidaError("No se puede sumar una cantidad negativa")
        return Cantidad(self.valor + cantidad)

    def restar(self, cantidad: int) -> Cantidad:
        if cantidad < 0:
            raise CantidadInvalidaError("No se puede restar una cantidad negativa")
        nuevo_valor = self.valor - cantidad
        if nuevo_valor < 0:
            raise StockInsuficienteError(disponible=self.valor, solicitado=cantidad)
        return Cantidad(nuevo_valor)

    def es_menor_que(self, otra: Cantidad) -> bool:
        return self.valor < otra.valor

    def es_mayor_que(self, otra: Cantidad) -> bool:
        return self.valor > otra.valor

    def es_menor_o_igual_que(self, otra: Cantidad) -> bool:
        return self.valor <= otra.valor

    def es_mayor_o_igual_que(self, otra: Cantidad) -> bool:
        return self.valor >= otra.valor

    def es_cero(self) -> bool:
        return self.valor == 0

    def es_positivo(self) -> bool:
        return self.valor > 0

    def __str__(self) -> str:
        return str(self.valor)