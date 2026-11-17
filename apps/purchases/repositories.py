from __future__ import annotations

from datetime import datetime

from django.db import transaction

from core.application.ports.purchases import CompraRepository, ProveedorRepository
from core.domain.purchases.entities import Compra, CompraDetalle, Proveedor
from core.domain.purchases.enums import EstadoCompra
from core.domain.shared.value_objects import Money, Quantity

from apps.purchases.models import (
    Compra as CompraORM,
    CompraDetalle as CompraDetalleORM,
    Proveedor as ProveedorORM,
)


def _proveedor_to_domain(orm: ProveedorORM) -> Proveedor:
    return Proveedor(
        id=orm.id,
        administrador_id=orm.administrador_id,
        nombre=orm.nombre,
        contacto=orm.contacto,
    )


def _detalle_to_domain(orm: CompraDetalleORM) -> CompraDetalle:
    return CompraDetalle(
        id=orm.id,
        compra_id=orm.compra_id,
        administrador_id=orm.administrador_id,
        producto_id=orm.producto_id,
        cantidad=Quantity(orm.cantidad),
        costo_unitario=Money(orm.costo_unitario),
    )


def _compra_to_domain(orm: CompraORM) -> Compra:
    return Compra(
        id=orm.id,
        administrador_id=orm.administrador_id,
        proveedor_id=orm.proveedor_id,
        usuario_id=orm.usuario_id,
        estado=EstadoCompra(orm.estado),
        nota=orm.nota,
        fecha=orm.fecha,
        _lineas=[_detalle_to_domain(detalle) for detalle in orm.detalles.all()],
    )


class DjangoProveedorRepository(ProveedorRepository):
    def obtener_por_id(self, proveedor_id: int) -> Proveedor | None:
        orm = ProveedorORM.objects.filter(pk=proveedor_id).first()
        return _proveedor_to_domain(orm) if orm else None

    def guardar(self, proveedor: Proveedor) -> Proveedor:
        defaults = {
            "administrador_id": proveedor.administrador_id,
            "nombre": proveedor.nombre,
            "contacto": proveedor.contacto,
        }
        if proveedor.id is None:
            orm = ProveedorORM.objects.create(**defaults)
        else:
            ProveedorORM.objects.filter(pk=proveedor.id).update(**defaults)
            orm = ProveedorORM.objects.get(pk=proveedor.id)
        proveedor.id = orm.id
        return proveedor

    def listar_por_administrador(self, administrador_id: int) -> list[Proveedor]:
        return [
            _proveedor_to_domain(orm)
            for orm in ProveedorORM.objects.filter(
                administrador_id=administrador_id
            ).order_by("nombre")
        ]

    def eliminar(self, proveedor_id: int) -> None:
        ProveedorORM.objects.filter(pk=proveedor_id).delete()


class DjangoCompraRepository(CompraRepository):
    def obtener_por_id(self, compra_id: int) -> Compra | None:
        orm = (
            CompraORM.objects.prefetch_related("detalles")
            .filter(pk=compra_id)
            .first()
        )
        return _compra_to_domain(orm) if orm else None

    @transaction.atomic
    def guardar(self, compra: Compra) -> Compra:
        defaults = {
            "administrador_id": compra.administrador_id,
            "proveedor_id": compra.proveedor_id,
            "usuario_id": compra.usuario_id,
            "fecha": compra.fecha,
            "total": compra.total.amount,
            "estado": compra.estado.value,
            "nota": compra.nota,
        }

        if compra.id is None:
            orm = CompraORM.objects.create(**defaults)
        else:
            CompraORM.objects.filter(pk=compra.id).update(**defaults)
            orm = CompraORM.objects.get(pk=compra.id)

        compra.id = orm.id
        compra.fecha = orm.fecha

        ids_existentes = set(
            CompraDetalleORM.objects.filter(compra_id=compra.id).values_list(
                "id", flat=True
            )
        )
        for linea in compra.lineas:
            linea_data = {
                "compra_id": compra.id,
                "administrador_id": compra.administrador_id,
                "producto_id": linea.producto_id,
                "cantidad": linea.cantidad.value,
                "costo_unitario": linea.costo_unitario.amount,
                "subtotal": linea.subtotal.amount,
            }
            if linea.id is None:
                detalle = CompraDetalleORM.objects.create(**linea_data)
                linea.id = detalle.id
            else:
                CompraDetalleORM.objects.filter(pk=linea.id).update(**linea_data)
                ids_existentes.discard(linea.id)
            linea.compra_id = compra.id

        if ids_existentes:
            CompraDetalleORM.objects.filter(id__in=ids_existentes).delete()

        return compra

    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        estado: EstadoCompra | None = None,
    ) -> list[Compra]:
        qs = (
            CompraORM.objects.prefetch_related("detalles")
            .filter(administrador_id=administrador_id)
            .order_by("-fecha")
        )
        if desde is not None:
            qs = qs.filter(fecha__gte=desde)
        if hasta is not None:
            qs = qs.filter(fecha__lte=hasta)
        if estado is not None:
            qs = qs.filter(estado=estado.value)
        return [_compra_to_domain(orm) for orm in qs]

    def eliminar(self, compra_id: int) -> None:
        CompraORM.objects.filter(pk=compra_id).delete()
