from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.domain.catalog.enums import MotivoMovimiento, ReferenciaTipo
from core.domain.catalog.exceptions import (
    CategoriaDeOtroAdministradorError,
    VigenciaInvalidaError,
)
from core.domain.catalog.value_objects import NombreCategoria, NombreProducto
from core.domain.shared.clock import now
from core.domain.shared.enums import TipoCliente
from core.domain.shared.errors import ValidationError
from core.domain.shared.value_objects import Money, Quantity


@dataclass
class Categoria:
    administrador_id: int
    nombre: NombreCategoria
    id: int | None = None

    def pertenece_a(self, administrador_id: int) -> bool:
        return self.administrador_id == administrador_id

    def renombrar(self, nombre: NombreCategoria) -> None:
        self.nombre = nombre


@dataclass
class Producto:
    administrador_id: int
    categoria_id: int
    nombre: NombreProducto
    id: int | None = None
    creado_en: datetime = field(default_factory=now)

    def pertenece_a(self, administrador_id: int) -> bool:
        return self.administrador_id == administrador_id

    def cambiar_categoria(self, categoria: Categoria) -> None:
        if categoria.id is None:
            raise ValidationError("La categoría debe estar persistida")
        if not categoria.pertenece_a(self.administrador_id):
            raise CategoriaDeOtroAdministradorError(
                categoria.id, self.administrador_id
            )
        self.categoria_id = categoria.id

    def renombrar(self, nombre: NombreProducto) -> None:
        self.nombre = nombre


@dataclass
class PrecioProducto:
    administrador_id: int
    producto_id: int
    tipo_cliente: TipoCliente
    precio: Money
    id: int | None = None
    vigente_desde: datetime = field(default_factory=now)
    vigente_hasta: datetime | None = None
    creado_en: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if self.vigente_hasta is not None and self.vigente_hasta <= self.vigente_desde:
            raise VigenciaInvalidaError()

    @property
    def moneda(self) -> str:
        return self.precio.currency

    def esta_vigente(self, momento: datetime | None = None) -> bool:
        momento = momento or now()
        if momento < self.vigente_desde:
            return False
        return self.vigente_hasta is None or momento < self.vigente_hasta

    def cerrar_vigencia(self, momento: datetime | None = None) -> None:
        if self.vigente_hasta is not None:
            raise ValidationError("La vigencia ya está cerrada")
        momento = momento or now()
        if momento <= self.vigente_desde:
            raise VigenciaInvalidaError()
        self.vigente_hasta = momento

    def cambiar_precio(self, nuevo_precio: Money) -> None:
        if self.vigente_hasta is not None:
            raise ValidationError("No se puede cambiar el precio de una tarifa histórica")
        self.precio = nuevo_precio


@dataclass
class MovimientoInventario:
    administrador_id: int
    producto_id: int
    motivo: MotivoMovimiento
    cantidad: Quantity
    usuario_id: int
    id: int | None = None
    fecha: datetime = field(default_factory=now)
    costo_unitario: Money | None = None
    precio_unitario: Money | None = None
    referencia_tipo: ReferenciaTipo | None = None
    referencia_id: int | None = None
    nota: str | None = None

    def __post_init__(self) -> None:
        if (self.referencia_tipo is None) != (self.referencia_id is None):
            raise ValidationError(
                "La referencia debe tener tipo e id, o ninguno de los dos"
            )
        if self.costo_unitario is not None and self.costo_unitario.amount < 0:
            raise ValidationError("El costo unitario no puede ser negativo")
        if self.precio_unitario is not None and self.precio_unitario.amount < 0:
            raise ValidationError("El precio unitario no puede ser negativo")

    @property
    def es_entrada(self) -> bool:
        return self.motivo.es_entrada

    @property
    def es_salida(self) -> bool:
        return self.motivo.es_salida

    @property
    def signo(self) -> int:
        return self.motivo.signo

    def cantidad_con_signo(self):
        from decimal import Decimal

        return Decimal(self.signo) * self.cantidad.value

    @classmethod
    def entrada_compra(
        cls,
        administrador_id: int,
        producto_id: int,
        cantidad: Quantity,
        costo_unitario: Money,
        usuario_id: int,
        compra_id: int,
        nota: str | None = None,
    ) -> MovimientoInventario:
        return cls(
            administrador_id=administrador_id,
            producto_id=producto_id,
            motivo=MotivoMovimiento.COMPRA,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            usuario_id=usuario_id,
            referencia_tipo=ReferenciaTipo.COMPRA,
            referencia_id=compra_id,
            nota=nota,
        )

    @classmethod
    def salida_venta(
        cls,
        administrador_id: int,
        producto_id: int,
        cantidad: Quantity,
        precio_unitario: Money,
        usuario_id: int,
        venta_id: int,
        nota: str | None = None,
    ) -> MovimientoInventario:
        return cls(
            administrador_id=administrador_id,
            producto_id=producto_id,
            motivo=MotivoMovimiento.VENTA,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            usuario_id=usuario_id,
            referencia_tipo=ReferenciaTipo.VENTA,
            referencia_id=venta_id,
            nota=nota,
        )

    @classmethod
    def devolucion(
        cls,
        administrador_id: int,
        producto_id: int,
        cantidad: Quantity,
        usuario_id: int,
        nota: str | None = None,
    ) -> MovimientoInventario:
        return cls(
            administrador_id=administrador_id,
            producto_id=producto_id,
            motivo=MotivoMovimiento.DEVOLUCION,
            cantidad=cantidad,
            usuario_id=usuario_id,
            nota=nota,
        )

    @classmethod
    def merma(
        cls,
        administrador_id: int,
        producto_id: int,
        cantidad: Quantity,
        usuario_id: int,
        nota: str | None = None,
    ) -> MovimientoInventario:
        return cls(
            administrador_id=administrador_id,
            producto_id=producto_id,
            motivo=MotivoMovimiento.MERMA,
            cantidad=cantidad,
            usuario_id=usuario_id,
            nota=nota,
        )

    @classmethod
    def ajuste(
        cls,
        administrador_id: int,
        producto_id: int,
        cantidad: Quantity,
        usuario_id: int,
        positivo: bool,
        nota: str | None = None,
    ) -> MovimientoInventario:
        return cls(
            administrador_id=administrador_id,
            producto_id=producto_id,
            motivo=(
                MotivoMovimiento.AJUSTE_POS if positivo else MotivoMovimiento.AJUSTE_NEG
            ),
            cantidad=cantidad,
            usuario_id=usuario_id,
            nota=nota,
        )
