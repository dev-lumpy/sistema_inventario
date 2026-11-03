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


@transaction.atomic
def registrar_salida_stock(*, producto, cantidad, canal_venta):
    return MovimientoStock.objects.create(
        producto=producto,
        tipo=MovimientoStock.TIPO_SALIDA,
        motivo=MovimientoStock.MOTIVO_VENTA,
        cantidad=cantidad,
        canal_venta=canal_venta,
        detalle=f'Venta por {canal_venta}',
    )
