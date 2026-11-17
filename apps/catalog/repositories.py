from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from core.application.ports.catalog import (
    CategoriaRepository,
    MovimientoInventarioRepository,
    PrecioProductoRepository,
    ProductoRepository,
)
from core.domain.catalog.entities import (
    Categoria,
    MovimientoInventario,
    PrecioProducto,
    Producto,
)
from core.domain.catalog.enums import MotivoMovimiento, ReferenciaTipo
from core.domain.catalog.value_objects import (
    NombreCategoria,
    NombreProducto,
    StockMinimo,
)
from core.domain.shared.clock import now
from core.domain.shared.enums import TipoCliente
from core.domain.shared.value_objects import Money, Quantity

from apps.catalog.models import (
    Categoria as CategoriaORM,
    MovimientoInventario as MovimientoORM,
    PrecioProducto as PrecioORM,
    Producto as ProductoORM,
)


def _categoria_to_domain(orm: CategoriaORM) -> Categoria:
    return Categoria(
        id=orm.id,
        administrador_id=orm.administrador_id,
        nombre=NombreCategoria(orm.nombre),
    )


def _producto_to_domain(orm: ProductoORM) -> Producto:
    return Producto(
        id=orm.id,
        administrador_id=orm.administrador_id,
        categoria_id=orm.categoria_id,
        nombre=NombreProducto(orm.nombre),
        stock_minimo=StockMinimo(orm.stock_minimo),
        creado_en=orm.creado_en,
    )


def _precio_to_domain(orm: PrecioORM) -> PrecioProducto:
    return PrecioProducto(
        id=orm.id,
        administrador_id=orm.administrador_id,
        producto_id=orm.producto_id,
        tipo_cliente=TipoCliente(orm.tipo_cliente),
        precio=Money(orm.precio, orm.moneda),
        vigente_desde=orm.vigente_desde,
        vigente_hasta=orm.vigente_hasta,
        creado_en=orm.creado_en,
    )


def _movimiento_to_domain(orm: MovimientoORM) -> MovimientoInventario:
    return MovimientoInventario(
        id=orm.id,
        administrador_id=orm.administrador_id,
        producto_id=orm.producto_id,
        motivo=MotivoMovimiento(orm.motivo),
        cantidad=Quantity(orm.cantidad),
        fecha=orm.fecha,
        costo_unitario=(
            Money(orm.costo_unitario) if orm.costo_unitario is not None else None
        ),
        precio_unitario=(
            Money(orm.precio_unitario) if orm.precio_unitario is not None else None
        ),
        referencia_tipo=(
            ReferenciaTipo(orm.referencia_tipo)
            if orm.referencia_tipo is not None
            else None
        ),
        referencia_id=orm.referencia_id,
        usuario_id=orm.usuario_id,
        nota=orm.nota,
    )


class DjangoCategoriaRepository(CategoriaRepository):
    def obtener_por_id(self, categoria_id: int) -> Categoria | None:
        orm = CategoriaORM.objects.filter(pk=categoria_id).first()
        return _categoria_to_domain(orm) if orm else None

    def guardar(self, categoria: Categoria) -> Categoria:
        if categoria.id is None:
            orm = CategoriaORM.objects.create(
                administrador_id=categoria.administrador_id,
                nombre=categoria.nombre.valor,
            )
        else:
            CategoriaORM.objects.filter(pk=categoria.id).update(
                administrador_id=categoria.administrador_id,
                nombre=categoria.nombre.valor,
            )
            orm = CategoriaORM.objects.get(pk=categoria.id)
        categoria.id = orm.id
        return categoria

    def listar_por_administrador(self, administrador_id: int) -> list[Categoria]:
        return [
            _categoria_to_domain(orm)
            for orm in CategoriaORM.objects.filter(
                administrador_id=administrador_id
            ).order_by("nombre")
        ]

    def eliminar(self, categoria_id: int) -> None:
        CategoriaORM.objects.filter(pk=categoria_id).delete()


class DjangoProductoRepository(ProductoRepository):
    def obtener_por_id(self, producto_id: int) -> Producto | None:
        orm = ProductoORM.objects.filter(pk=producto_id).first()
        return _producto_to_domain(orm) if orm else None

    def guardar(self, producto: Producto) -> Producto:
        defaults = {
            "administrador_id": producto.administrador_id,
            "categoria_id": producto.categoria_id,
            "nombre": producto.nombre.valor,
            "stock_minimo": producto.stock_minimo.valor,
            "creado_en": producto.creado_en,
        }
        if producto.id is None:
            orm = ProductoORM.objects.create(**defaults)
        else:
            ProductoORM.objects.filter(pk=producto.id).update(**defaults)
            orm = ProductoORM.objects.get(pk=producto.id)
        producto.id = orm.id
        producto.creado_en = orm.creado_en
        return producto

    def listar_por_administrador(self, administrador_id: int) -> list[Producto]:
        return [
            _producto_to_domain(orm)
            for orm in ProductoORM.objects.filter(
                administrador_id=administrador_id
            ).order_by("nombre")
        ]

    def buscar_por_nombre(
        self, administrador_id: int, texto: str
    ) -> list[Producto]:
        return [
            _producto_to_domain(orm)
            for orm in ProductoORM.objects.filter(
                administrador_id=administrador_id,
                nombre__icontains=texto,
            ).order_by("nombre")
        ]

    def eliminar(self, producto_id: int) -> None:
        ProductoORM.objects.filter(pk=producto_id).delete()


class DjangoPrecioProductoRepository(PrecioProductoRepository):
    def obtener_por_id(self, precio_id: int) -> PrecioProducto | None:
        orm = PrecioORM.objects.filter(pk=precio_id).first()
        return _precio_to_domain(orm) if orm else None

    def obtener_vigente(
        self,
        producto_id: int,
        administrador_id: int,
        tipo_cliente: TipoCliente,
        momento: datetime | None = None,
    ) -> PrecioProducto | None:
        momento = momento or now()
        orm = (
            PrecioORM.objects.filter(
                producto_id=producto_id,
                administrador_id=administrador_id,
                tipo_cliente=tipo_cliente.value,
                vigente_desde__lte=momento,
                vigente_hasta__isnull=True,
            )
            .order_by("-vigente_desde")
            .first()
        )
        return _precio_to_domain(orm) if orm else None

    def guardar(self, precio: PrecioProducto) -> PrecioProducto:
        defaults = {
            "administrador_id": precio.administrador_id,
            "producto_id": precio.producto_id,
            "tipo_cliente": precio.tipo_cliente.value,
            "precio": precio.precio.amount,
            "moneda": precio.precio.currency,
            "vigente_desde": precio.vigente_desde,
            "vigente_hasta": precio.vigente_hasta,
            "creado_en": precio.creado_en,
        }
        if precio.id is None:
            orm = PrecioORM.objects.create(**defaults)
        else:
            PrecioORM.objects.filter(pk=precio.id).update(**defaults)
            orm = PrecioORM.objects.get(pk=precio.id)
        precio.id = orm.id
        return precio

    def listar_por_producto(
        self, producto_id: int, administrador_id: int
    ) -> list[PrecioProducto]:
        return [
            _precio_to_domain(orm)
            for orm in PrecioORM.objects.filter(
                producto_id=producto_id,
                administrador_id=administrador_id,
            ).order_by("-vigente_desde")
        ]

    def cerrar_vigencia(self, precio_id: int, momento: datetime | None = None) -> None:
        PrecioORM.objects.filter(pk=precio_id, vigente_hasta__isnull=True).update(
            vigente_hasta=momento or now()
        )


class DjangoMovimientoInventarioRepository(MovimientoInventarioRepository):
    def guardar(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        orm = MovimientoORM.objects.create(
            administrador_id=movimiento.administrador_id,
            producto_id=movimiento.producto_id,
            motivo=movimiento.motivo.value,
            cantidad=movimiento.cantidad.value,
            fecha=movimiento.fecha,
            costo_unitario=(
                movimiento.costo_unitario.amount
                if movimiento.costo_unitario is not None
                else None
            ),
            precio_unitario=(
                movimiento.precio_unitario.amount
                if movimiento.precio_unitario is not None
                else None
            ),
            referencia_tipo=(
                movimiento.referencia_tipo.value
                if movimiento.referencia_tipo is not None
                else None
            ),
            referencia_id=movimiento.referencia_id,
            usuario_id=movimiento.usuario_id,
            nota=movimiento.nota,
        )
        movimiento.id = orm.id
        movimiento.fecha = orm.fecha
        return movimiento

    def listar_por_producto(
        self, producto_id: int, administrador_id: int
    ) -> list[MovimientoInventario]:
        return [
            _movimiento_to_domain(orm)
            for orm in MovimientoORM.objects.filter(
                producto_id=producto_id,
                administrador_id=administrador_id,
            ).order_by("-fecha")
        ]

    def listar_por_periodo(
        self, administrador_id: int, desde: datetime, hasta: datetime
    ) -> list[MovimientoInventario]:
        return [
            _movimiento_to_domain(orm)
            for orm in MovimientoORM.objects.filter(
                administrador_id=administrador_id,
                fecha__gte=desde,
                fecha__lte=hasta,
            ).order_by("-fecha")
        ]

    def calcular_stock(self, producto_id: int, administrador_id: int) -> Decimal:
        total = Decimal("0")
        filas = MovimientoORM.objects.filter(
            producto_id=producto_id,
            administrador_id=administrador_id,
        ).values_list("motivo", "cantidad")
        for motivo, cantidad in filas:
            signo = MotivoMovimiento(motivo).signo
            total += signo * Decimal(cantidad)
        return total
