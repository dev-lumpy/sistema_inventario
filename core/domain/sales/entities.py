from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.domain.sales.enums import CanalVenta, EstadoVenta
from core.domain.sales.exceptions import (
    LineaDeOtroAdministradorError,
    TransicionVentaInvalidaError,
    VentaConfirmadaNoEliminableError,
    VentaNoEditableError,
    VentaSinLineasError,
)
from core.domain.shared.clock import now
from core.domain.shared.enums import TipoCliente
from core.domain.shared.errors import ValidationError
from core.domain.shared.validators import texto_opcional
from core.domain.shared.value_objects import Money, Quantity


@dataclass
class VentaDetalle:
    administrador_id: int
    producto_id: int
    cantidad: Quantity
    precio_unitario: Money
    id: int | None = None
    venta_id: int | None = None

    @property
    def subtotal(self) -> Money:
        return self.precio_unitario * self.cantidad

    def pertenece_a(self, administrador_id: int) -> bool:
        return self.administrador_id == administrador_id

    def cambiar_cantidad(self, cantidad: Quantity) -> None:
        self.cantidad = cantidad

    def cambiar_precio(self, precio_unitario: Money) -> None:
        self.precio_unitario = precio_unitario


@dataclass
class Venta:
    administrador_id: int
    vendedor_id: int
    tipo_cliente: TipoCliente
    canal_venta: CanalVenta | None = None
    moneda: str = "BOB"
    cliente_nombre: str | None = None
    estado: EstadoVenta = EstadoVenta.BORRADOR
    nota: str | None = None
    id: int | None = None
    fecha: datetime = field(default_factory=now)
    _lineas: list[VentaDetalle] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.canal_venta, str):
            self.canal_venta = CanalVenta.desde(self.canal_venta)
        self.moneda = str(self.moneda or "BOB").strip().upper()
        if len(self.moneda) != 3 or not self.moneda.isalpha():
            raise ValidationError("La moneda de la venta debe tener 3 letras")
        self.cliente_nombre = texto_opcional(self.cliente_nombre, "cliente", 150)
        self.nota = texto_opcional(self.nota, "nota", 1000)

    @property
    def lineas(self) -> tuple[VentaDetalle, ...]:
        return tuple(self._lineas)

    @property
    def total(self) -> Money:
        if not self._lineas:
            return Money.cero(self.moneda)
        total = Money.cero(self.moneda)
        for linea in self._lineas:
            if linea.precio_unitario.currency != self.moneda:
                raise ValidationError("No se pueden mezclar monedas en una venta")
            total = total + linea.subtotal
        return total

    @property
    def esta_confirmada(self) -> bool:
        return self.estado == EstadoVenta.CONFIRMADA

    @property
    def es_borrador(self) -> bool:
        return self.estado == EstadoVenta.BORRADOR

    @property
    def esta_anulada(self) -> bool:
        return self.estado == EstadoVenta.ANULADA

    def agregar_linea(
        self,
        producto_id: int,
        cantidad: Quantity,
        precio_unitario: Money,
        administrador_id: int | None = None,
    ) -> VentaDetalle:
        self._exigir_borrador()
        if administrador_id is not None and administrador_id != self.administrador_id:
            raise LineaDeOtroAdministradorError(administrador_id)
        if precio_unitario.currency != self.moneda:
            raise ValidationError("La moneda de la línea no coincide con la venta")
        detalle = VentaDetalle(
            administrador_id=self.administrador_id,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            venta_id=self.id,
        )
        self._lineas.append(detalle)
        return detalle

    def quitar_linea(self, producto_id: int) -> None:
        self._exigir_borrador()
        self._lineas = [
            linea for linea in self._lineas if linea.producto_id != producto_id
        ]

    def confirmar(self) -> None:
        if not self.es_borrador:
            raise TransicionVentaInvalidaError(self.estado.value, "confirmar")
        if not self._lineas:
            raise VentaSinLineasError()
        self.estado = EstadoVenta.CONFIRMADA

    def anular(self) -> None:
        if self.esta_anulada:
            raise TransicionVentaInvalidaError(self.estado.value, "anular")
        self.estado = EstadoVenta.ANULADA

    def puede_eliminarse(self) -> bool:
        return not self.esta_confirmada

    def verificar_eliminable(self) -> None:
        if self.esta_confirmada:
            raise VentaConfirmadaNoEliminableError(self.id)

    def requiere_reversion_stock(self) -> bool:
        return self.esta_confirmada

    def _exigir_borrador(self) -> None:
        if not self.es_borrador:
            raise VentaNoEditableError(self.estado.value)
