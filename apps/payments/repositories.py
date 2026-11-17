from __future__ import annotations

from datetime import datetime

from core.application.ports.payments import PagoRepository
from core.domain.payments.entities import Pago
from core.domain.payments.enums import MetodoPago
from core.domain.shared.value_objects import Money

from apps.payments.models import Pago as PagoORM


def _pago_to_domain(orm: PagoORM) -> Pago:
    return Pago(
        id=orm.id,
        administrador_id=orm.administrador_id,
        venta_id=orm.venta_id,
        metodo=MetodoPago(orm.metodo),
        monto=Money(orm.monto, orm.moneda),
        fecha=orm.fecha,
    )


class DjangoPagoRepository(PagoRepository):
    def obtener_por_id(self, pago_id: int) -> Pago | None:
        orm = PagoORM.objects.filter(pk=pago_id).first()
        return _pago_to_domain(orm) if orm else None

    def guardar(self, pago: Pago) -> Pago:
        defaults = {
            "administrador_id": pago.administrador_id,
            "venta_id": pago.venta_id,
            "metodo": pago.metodo.value,
            "monto": pago.monto.amount,
            "moneda": pago.monto.currency,
            "fecha": pago.fecha,
        }
        if pago.id is None:
            orm = PagoORM.objects.create(**defaults)
        else:
            PagoORM.objects.filter(pk=pago.id).update(**defaults)
            orm = PagoORM.objects.get(pk=pago.id)
        pago.id = orm.id
        pago.fecha = orm.fecha
        return pago

    def listar_por_venta(self, venta_id: int) -> list[Pago]:
        return [
            _pago_to_domain(orm)
            for orm in PagoORM.objects.filter(venta_id=venta_id).order_by("fecha")
        ]

    def listar_por_administrador(
        self,
        administrador_id: int,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[Pago]:
        qs = PagoORM.objects.filter(administrador_id=administrador_id).order_by("fecha")
        if desde is not None:
            qs = qs.filter(fecha__gte=desde)
        if hasta is not None:
            qs = qs.filter(fecha__lte=hasta)
        return [_pago_to_domain(orm) for orm in qs]

    def eliminar(self, pago_id: int) -> None:
        PagoORM.objects.filter(pk=pago_id).delete()
