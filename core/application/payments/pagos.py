from __future__ import annotations

from decimal import Decimal

from core.application.ports.unit_of_work import UnitOfWork
from core.domain.payments.entities import Pago
from core.domain.payments.enums import MetodoPago
from core.domain.shared.errors import BusinessRuleViolation, NotFoundError
from core.domain.shared.value_objects import Money


class RegistrarPago:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        administrador_id: int,
        venta_id: int,
        metodo: str,
        monto,
    ) -> Pago:
        venta = self._uow.ventas.obtener_por_id(venta_id)
        if venta is None:
            raise NotFoundError("La venta no existe")
        if venta.administrador_id != administrador_id:
            raise BusinessRuleViolation("La venta pertenece a otro administrador")
        if not venta.esta_confirmada:
            raise BusinessRuleViolation("Solo se puede cobrar una venta confirmada")

        pagado = sum(
            (pago.monto.amount for pago in self._uow.pagos.listar_por_venta(venta_id)),
            Decimal("0"),
        )
        nuevo = Money(Decimal(str(monto)))
        if pagado + nuevo.amount > venta.total.amount:
            raise BusinessRuleViolation(
                "El pago supera el total de la venta",
                total=str(venta.total.amount),
                pagado=str(pagado),
                nuevo=str(nuevo.amount),
            )

        pago = Pago(
            administrador_id=administrador_id,
            venta_id=venta_id,
            metodo=MetodoPago(metodo),
            monto=nuevo,
        )
        return self._uow.pagos.guardar(pago)
