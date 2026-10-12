# apps/inventario/services/movimiento_service.py
from django.db import transaction
from apps.inventario.models import MovimientoStock


@transaction.atomic
def registrar_entrada_stock(*, producto, cantidad, proveedor):
    return MovimientoStock.objects.create(
        producto=producto,
        proveedor=proveedor,
        tipo=MovimientoStock.TIPO_ENTRADA,
        motivo=MovimientoStock.MOTIVO_COMPRA,
        cantidad=cantidad,
        detalle=f'Compra a {proveedor.nombre}',
    )
