# apps/inventario/services/reportes.py
from django.db.models import Sum, Q
from apps.inventario.models import MovimientoStock, Producto


def productos_vendidos_en_rango(desde, hasta):
    return (
        Producto.objects
        .annotate(
            cantidad_vendida=Sum(
                'movimientos__cantidad',
                filter=Q(
                    movimientos__tipo=MovimientoStock.TIPO_SALIDA,
                    movimientos__motivo=MovimientoStock.MOTIVO_VENTA,
                    movimientos__fecha__date__gte=desde,
                    movimientos__fecha__date__lte=hasta,
                ),
            ),
        )
        .filter(cantidad_vendida__gt=0)
        .order_by('-cantidad_vendida', 'nombre')
    )


def resumen_periodo(desde, hasta):
    qs = MovimientoStock.objects.filter(
        fecha__date__gte=desde,
        fecha__date__lte=hasta,
    )
    entradas = qs.filter(tipo=MovimientoStock.TIPO_ENTRADA).aggregate(
        total=Sum("cantidad")
    )["total"] or 0
    salidas = qs.filter(tipo=MovimientoStock.TIPO_SALIDA).aggregate(
        total=Sum("cantidad")
    )["total"] or 0
    return {"desde": desde, "hasta": hasta, "entradas": entradas, "salidas": salidas}
