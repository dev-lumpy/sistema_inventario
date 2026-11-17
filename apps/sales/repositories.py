from __future__ import annotations

from datetime import datetime

from django.db import transaction

from core.application.ports.sales import VentaRepository
from core.domain.sales.entities import Venta, VentaDetalle
from core.domain.sales.enums import CanalVenta, EstadoVenta
from core.domain.shared.enums import TipoCliente
from core.domain.shared.value_objects import Money, Quantity

from apps.sales.models import Venta as VentaORM, VentaDetalle as VentaDetalleORM


def _detalle_to_domain(orm: VentaDetalleORM, moneda: str) -> VentaDetalle:
    return VentaDetalle(
        id=orm.id,
        venta_id=orm.venta_id,
        administrador_id=orm.administrador_id,
        producto_id=orm.producto_id,
        cantidad=Quantity(orm.cantidad),
        precio_unitario=Money(orm.precio_unitario, moneda),
    )


def _venta_to_domain(orm: VentaORM) -> Venta:
    lineas = [
        _detalle_to_domain(detalle, orm.moneda) for detalle in orm.detalles.all()
    ]
    return Venta(
        id=orm.id,
        administrador_id=orm.administrador_id,
        vendedor_id=orm.vendedor_id,
        tipo_cliente=TipoCliente(orm.tipo_cliente),
        canal_venta=CanalVenta(orm.canal_venta) if orm.canal_venta else None,
        moneda=orm.moneda,
        cliente_nombre=orm.cliente_nombre,
        estado=EstadoVenta(orm.estado),
        nota=orm.nota,
        fecha=orm.fecha,
        _lineas=lineas,
    )


class DjangoVentaRepository(VentaRepository):
    def obtener_por_id(self, venta_id: int) -> Venta | None:
        orm = (
            VentaORM.objects.prefetch_related("detalles")
            .filter(pk=venta_id)
            .first()
        )
        return _venta_to_domain(orm) if orm else None

    @transaction.atomic
    def guardar(self, venta: Venta) -> Venta:
        defaults = {
            "administrador_id": venta.administrador_id,
            "vendedor_id": venta.vendedor_id,
            "cliente_nombre": venta.cliente_nombre,
            "tipo_cliente": venta.tipo_cliente.value,
            "canal_venta": venta.canal_venta.value if venta.canal_venta else None,
            "moneda": venta.moneda,
            "fecha": venta.fecha,
            "total": venta.total.amount,
            "estado": venta.estado.value,
            "nota": venta.nota,
        }

        if venta.id is None:
            orm = VentaORM.objects.create(**defaults)
        else:
            VentaORM.objects.filter(pk=venta.id).update(**defaults)
            orm = VentaORM.objects.get(pk=venta.id)

        venta.id = orm.id
        venta.fecha = orm.fecha

        ids_existentes = set(
            VentaDetalleORM.objects.filter(venta_id=venta.id).values_list(
                "id", flat=True
            )
        )
        for linea in venta.lineas:
            linea_data = {
                "venta_id": venta.id,
                "administrador_id": venta.administrador_id,
                "producto_id": linea.producto_id,
                "cantidad": linea.cantidad.value,
                "precio_unitario": linea.precio_unitario.amount,
                "subtotal": linea.subtotal.amount,
            }
            if linea.id is None:
                detalle = VentaDetalleORM.objects.create(**linea_data)
                linea.id = detalle.id
            else:
                VentaDetalleORM.objects.filter(pk=linea.id).update(**linea_data)
                ids_existentes.discard(linea.id)
            linea.venta_id = venta.id

        if ids_existentes:
            VentaDetalleORM.objects.filter(id__in=ids_existentes).delete()

        return venta

    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        estado: EstadoVenta | None = None,
    ) -> list[Venta]:
        qs = (
            VentaORM.objects.prefetch_related("detalles")
            .filter(administrador_id=administrador_id)
            .order_by("-fecha")
        )
        if desde is not None:
            qs = qs.filter(fecha__gte=desde)
        if hasta is not None:
            qs = qs.filter(fecha__lte=hasta)
        if estado is not None:
            qs = qs.filter(estado=estado.value)
        return [_venta_to_domain(orm) for orm in qs]

    def eliminar(self, venta_id: int) -> None:
        VentaORM.objects.filter(pk=venta_id).delete()
