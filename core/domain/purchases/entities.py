from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.domain.purchases.enums import EstadoCompra
from core.domain.purchases.exceptions import (
    CompraNoEditableError,
    CompraSinLineasError,
    LineaDeCompraDeOtroAdministradorError,
    ProveedorDeOtroAdministradorError,
    TransicionCompraInvalidaError,
)
from core.domain.shared.clock import now
from core.domain.shared.errors import ValidationError
from core.domain.shared.validators import texto_opcional, texto_requerido
from core.domain.shared.value_objects import Money, Quantity


@dataclass
class Proveedor:
    administrador_id: int
    nombre: str
    id: int | None = None
    contacto: str | None = None

    def __post_init__(self) -> None:
        self.nombre = texto_requerido(self.nombre, "proveedor", 150)
        self.contacto = texto_opcional(self.contacto, "contacto", 150)

    def pertenece_a(self, administrador_id: int) -> bool:
        return self.administrador_id == administrador_id

    def verificar_administrador(self, administrador_id: int) -> None:
        if not self.pertenece_a(administrador_id):
            raise ProveedorDeOtroAdministradorError(self.id or 0, administrador_id)


@dataclass
class CompraDetalle:
    administrador_id: int
    producto_id: int
    cantidad: Quantity
    costo_unitario: Money
    id: int | None = None
    compra_id: int | None = None

    @property
    def subtotal(self) -> Money:
        return self.costo_unitario * self.cantidad


@dataclass
class Compra:
    administrador_id: int
    proveedor_id: int
    usuario_id: int
    estado: EstadoCompra = EstadoCompra.BORRADOR
    nota: str | None = None
    id: int | None = None
    fecha: datetime = field(default_factory=now)
    _lineas: list[CompraDetalle] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.nota = texto_opcional(self.nota, "nota", 1000)

    @property
    def lineas(self) -> tuple[CompraDetalle, ...]:
        return tuple(self._lineas)

    @property
    def total(self) -> Money:
        if not self._lineas:
            return Money.cero()
        moneda = self._lineas[0].costo_unitario.currency
        total = Money.cero(moneda)
        for linea in self._lineas:
            if linea.costo_unitario.currency != moneda:
                raise ValidationError("No se pueden mezclar monedas en una compra")
            total = total + linea.subtotal
        return total

    @property
    def es_borrador(self) -> bool:
        return self.estado == EstadoCompra.BORRADOR

    @property
    def esta_confirmada(self) -> bool:
        return self.estado == EstadoCompra.CONFIRMADA

    def agregar_linea(
        self,
        producto_id: int,
        cantidad: Quantity,
        costo_unitario: Money,
        administrador_id: int | None = None,
    ) -> CompraDetalle:
        self._exigir_borrador()
        if administrador_id is not None and administrador_id != self.administrador_id:
            raise LineaDeCompraDeOtroAdministradorError(administrador_id)
        detalle = CompraDetalle(
            administrador_id=self.administrador_id,
            producto_id=producto_id,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            compra_id=self.id,
        )
        self._lineas.append(detalle)
        return detalle

    def quitar_linea(self, producto_id: int) -> None:
        self._exigir_borrador()
        self._lineas = [
            linea for linea in self._lineas if linea.producto_id != producto_id
        ]

    def confirmar(self, proveedor: Proveedor | None = None) -> None:
        if not self.es_borrador:
            raise TransicionCompraInvalidaError(self.estado.value, "confirmar")
        if not self._lineas:
            raise CompraSinLineasError()
        if proveedor is not None:
            proveedor.verificar_administrador(self.administrador_id)
        self.estado = EstadoCompra.CONFIRMADA

    def anular(self) -> None:
        if self.estado == EstadoCompra.ANULADA:
            raise TransicionCompraInvalidaError(self.estado.value, "anular")
        self.estado = EstadoCompra.ANULADA

    def _exigir_borrador(self) -> None:
        if not self.es_borrador:
            raise CompraNoEditableError(self.estado.value)
