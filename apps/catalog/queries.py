from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from apps.catalog.models import (
    Categoria as CategoriaORM,
    MovimientoInventario as MovimientoORM,
    PrecioProducto as PrecioORM,
    Producto as ProductoORM,
)
from apps.purchases.models import Compra as CompraORM
from core.domain.catalog.enums import MotivoMovimiento


def _stock_por_producto(administrador_id: int) -> dict[int, Decimal]:
    stock: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    filas = MovimientoORM.objects.filter(
        administrador_id=administrador_id
    ).values_list("producto_id", "motivo", "cantidad")
    for producto_id, motivo, cantidad in filas:
        stock[producto_id] += MotivoMovimiento(motivo).signo * Decimal(cantidad)
    return stock


def _precios_individuales(administrador_id: int) -> dict[int, tuple[Decimal, str]]:
    precios: dict[int, tuple[Decimal, str]] = {}
    filas = PrecioORM.objects.filter(
        administrador_id=administrador_id,
        tipo_cliente="individual",
        vigente_hasta__isnull=True,
    ).values_list("producto_id", "precio", "moneda")
    for producto_id, precio, moneda in filas:
        precios[producto_id] = (Decimal(precio), moneda)
    return precios


def listar_inventario(administrador_id: int) -> list[dict]:
    stock = _stock_por_producto(administrador_id)
    precios = _precios_individuales(administrador_id)
    productos = ProductoORM.objects.filter(
        administrador_id=administrador_id
    ).order_by("nombre")
    return [
        {
            "id": producto.id,
            "nombre": producto.nombre,
            "categoria": producto.categoria_id,
            "precio_unitario": float(
                precios.get(producto.id, (Decimal("0"), "BOB"))[0]
            ),
            "moneda": precios.get(producto.id, (Decimal("0"), "BOB"))[1],
            "stock_minimo": float(producto.stock_minimo),
            "stock_actual": float(stock.get(producto.id, Decimal("0"))),
            "activo": True,
        }
        for producto in productos
    ]


def alertas_stock(administrador_id: int) -> list[dict]:
    stock = _stock_por_producto(administrador_id)
    productos = ProductoORM.objects.filter(
        administrador_id=administrador_id
    ).order_by("nombre")
    resultado = []
    for producto in productos:
        actual = stock.get(producto.id, Decimal("0"))
        if actual <= producto.stock_minimo:
            resultado.append(
                {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "stock": float(actual),
                    "stock_minimo": float(producto.stock_minimo),
                }
            )
    return resultado


def _resumen_entre(administrador_id: int, desde: date, hasta: date) -> dict:
    filas = MovimientoORM.objects.filter(
        administrador_id=administrador_id,
        fecha__date__gte=desde,
        fecha__date__lte=hasta,
    ).values_list("motivo", "cantidad")

    entradas = Decimal("0")
    salidas = Decimal("0")
    for motivo, cantidad in filas:
        valor = Decimal(cantidad)
        if MotivoMovimiento(motivo).es_entrada:
            entradas += valor
        else:
            salidas += valor

    return {
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "entradas": float(entradas),
        "salidas": float(salidas),
    }


def resumen_hoy(administrador_id: int) -> dict:
    hoy = timezone.localdate()
    resumen = _resumen_entre(administrador_id, hoy, hoy)
    return {"ventas": resumen["salidas"], "entradas": resumen["entradas"]}


def resumen_periodo(administrador_id: int, desde: date, hasta: date) -> dict:
    return _resumen_entre(administrador_id, desde, hasta)


def productos_vendidos(
    administrador_id: int, desde: date | None = None, hasta: date | None = None
) -> list[dict]:
    qs = MovimientoORM.objects.filter(
        administrador_id=administrador_id,
        motivo=MotivoMovimiento.VENTA.value,
    )
    if desde is not None:
        qs = qs.filter(fecha__date__gte=desde)
    if hasta is not None:
        qs = qs.filter(fecha__date__lte=hasta)

    cantidades: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
    for producto_id, cantidad in qs.values_list("producto_id", "cantidad"):
        cantidades[producto_id] += Decimal(cantidad)

    productos = ProductoORM.objects.filter(id__in=cantidades.keys())
    nombres = {producto.id: producto.nombre for producto in productos}
    resultado = [
        {
            "id": producto_id,
            "nombre": nombres.get(producto_id, "—"),
            "cantidad_vendida": float(cantidad),
        }
        for producto_id, cantidad in cantidades.items()
        if cantidad > 0
    ]
    return sorted(
        resultado, key=lambda item: (-item["cantidad_vendida"], item["nombre"])
    )


def productos_mas_vendidos(administrador_id: int) -> list[dict]:
    return productos_vendidos(administrador_id)


def _proveedores_por_compra(compra_ids: list[int]) -> dict[int, str]:
    if not compra_ids:
        return {}
    compras = CompraORM.objects.filter(id__in=compra_ids).select_related("proveedor")
    return {compra.id: compra.proveedor.nombre for compra in compras}


def historial_movimientos(administrador_id: int, limite: int = 100) -> list[dict]:
    limite = max(1, min(int(limite), 100))
    movimientos = list(
        MovimientoORM.objects.filter(administrador_id=administrador_id)
        .select_related("producto", "producto__categoria")
        .order_by("-fecha")[:limite]
    )
    compra_ids = [
        movimiento.referencia_id
        for movimiento in movimientos
        if movimiento.referencia_tipo == "compra" and movimiento.referencia_id
    ]
    proveedores = _proveedores_por_compra(compra_ids)

    return [
        {
            "id": movimiento.id,
            "categoria": movimiento.producto.categoria.nombre,
            "producto": movimiento.producto.nombre,
            "cantidad": float(movimiento.cantidad),
            "proveedor": (
                proveedores.get(movimiento.referencia_id, "—")
                if movimiento.referencia_tipo == "compra"
                else "—"
            ),
            "motivo": movimiento.motivo,
            "fecha": movimiento.fecha.isoformat(),
        }
        for movimiento in movimientos
    ]


def historial_entradas(administrador_id: int) -> list[dict]:
    movimientos = list(
        MovimientoORM.objects.filter(
            administrador_id=administrador_id,
            motivo=MotivoMovimiento.COMPRA.value,
        )
        .select_related("producto")
        .order_by("-fecha")
    )
    compra_ids = [
        movimiento.referencia_id
        for movimiento in movimientos
        if movimiento.referencia_tipo == "compra" and movimiento.referencia_id
    ]
    proveedores = _proveedores_por_compra(compra_ids)
    return [
        {
            "id": movimiento.id,
            "producto": movimiento.producto.nombre,
            "cantidad": float(movimiento.cantidad),
            "proveedor": (
                proveedores.get(movimiento.referencia_id, "—")
                if movimiento.referencia_tipo == "compra"
                else "—"
            ),
            "fecha": movimiento.fecha.isoformat(),
        }
        for movimiento in movimientos
    ]


def productos_para_historial(administrador_id: int) -> list[dict]:
    productos = ProductoORM.objects.filter(
        administrador_id=administrador_id
    ).select_related("categoria").order_by("nombre")
    return [
        {
            "id": producto.id,
            "nombre": producto.nombre,
            "categoria": producto.categoria.nombre,
        }
        for producto in productos
    ]


def categorias_de(administrador_id: int) -> list[dict]:
    return [
        {"id": categoria.id, "nombre": categoria.nombre}
        for categoria in CategoriaORM.objects.filter(
            administrador_id=administrador_id
        ).order_by("nombre")
    ]


def parse_fecha(valor: str | None) -> date | None:
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        from core.domain.shared.errors import ValidationError

        raise ValidationError("La fecha debe tener formato YYYY-MM-DD") from exc
