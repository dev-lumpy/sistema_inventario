# tests/infrastructure/http/test_productos_vendidos_en_rango.py
"""
Test de integración de:
    GET /api/inventario/productos/vendidos/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD

No usa mocks: crea productos y movimientos reales en la BD de test,
autentica con un JWT real y consulta el endpoint.
"""

import json
from datetime import datetime

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.inventario.models import Categoria, MovimientoStock, Producto
from apps.usuarios.models import AdministradorORM


URL_PRODUCTOS_VENDIDOS = "/api/inventario/productos/vendidos/"


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def api_client() -> APIClient:
    admin = AdministradorORM.objects.create(
        username="admin_vendidos_rango",
        email="admin_vendidos_rango@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )

    client = APIClient()
    token = AccessToken.for_user(admin)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def productos_con_ventas_en_octubre():
    categoria = Categoria.objects.create(nombre="Frenos Rango Test")

    def crear_producto(nombre: str) -> Producto:
        return Producto.objects.create(
            nombre=nombre,
            categoria=categoria,
            precio_unitario="1000.00",
            stock_minimo=1,
            activo=True,
        )

    def crear_movimiento(producto, tipo, motivo, cantidad, fecha, canal=None):
        movimiento = MovimientoStock.objects.create(
            producto=producto,
            tipo=tipo,
            motivo=motivo,
            cantidad=cantidad,
            canal_venta=canal,
            detalle=f"Movimiento {motivo} del test",
        )
        # auto_now_add ignora el valor en el create; lo forzamos por SQL.
        MovimientoStock.objects.filter(pk=movimiento.pk).update(fecha=fecha)
        return movimiento

    def en_fecha(anio: int, mes: int, dia: int):
        return timezone.make_aware(datetime(anio, mes, dia, 12, 0))

    producto_a = crear_producto("Producto A")
    producto_b = crear_producto("Producto B")
    producto_c = crear_producto("Producto C")
    producto_d = crear_producto("Producto D")

    for producto, stock in (
        (producto_a, 500),
        (producto_b, 300),
        (producto_c, 200),
        (producto_d, 200),
    ):
        crear_movimiento(
            producto,
            MovimientoStock.TIPO_ENTRADA,
            MovimientoStock.MOTIVO_INICIAL,
            stock,
            en_fecha(2026, 9, 1),
        )

    # Producto A: 70 + 50 = 120 dentro de octubre
    crear_movimiento(
        producto_a, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        70, en_fecha(2026, 10, 5), canal="whatsapp",
    )
    crear_movimiento(
        producto_a, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        50, en_fecha(2026, 10, 20), canal="presencial",
    )

    # Producto B: 80 dentro de octubre
    crear_movimiento(
        producto_b, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        80, en_fecha(2026, 10, 10), canal="instagram",
    )

    # Producto C: 35 el último día del rango (debe incluirse)
    crear_movimiento(
        producto_c, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        35, en_fecha(2026, 10, 31), canal="facebook",
    )

    # Producto D: ventas fuera del rango (no deben contar)
    crear_movimiento(
        producto_d, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        40, en_fecha(2026, 9, 30), canal="otro",
    )
    crear_movimiento(
        producto_d, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        40, en_fecha(2026, 11, 1), canal="otro",
    )

    # Ruido: una merma en octubre NO debe contar como venta
    crear_movimiento(
        producto_a, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_MERMA,
        5, en_fecha(2026, 10, 15),
    )

    return {
        "producto_a": producto_a,
        "producto_b": producto_b,
        "producto_c": producto_c,
        "producto_d": producto_d,
    }


# =========================================================================
# GET: productos vendidos en un rango de fechas
# =========================================================================

@pytest.mark.django_db
def test_get_devuelve_productos_vendidos_en_el_rango(
    api_client,
    productos_con_ventas_en_octubre,
):
    """
    Si falla: el endpoint no filtra bien por fechas, no excluye mermas
    o no suma/ordena las cantidades vendidas.
    """

    query = "?desde=2026-10-01&hasta=2026-10-31"

    response = api_client.get(f"{URL_PRODUCTOS_VENDIDOS}{query}")

    # ------------------------------------------------------------------
    # JSON que ESPERAMOS recibir
    # ------------------------------------------------------------------
    respuesta_esperada = [
        {
            "id": productos_con_ventas_en_octubre["producto_a"].id,
            "nombre": "Producto A",
            "cantidad_vendida": 120,
        },
        {
            "id": productos_con_ventas_en_octubre["producto_b"].id,
            "nombre": "Producto B",
            "cantidad_vendida": 80,
        },
        {
            "id": productos_con_ventas_en_octubre["producto_c"].id,
            "nombre": "Producto C",
            "cantidad_vendida": 35,
        },
    ]

    assert response.status_code == 200
    assert json.loads(response.content) == respuesta_esperada

    # Producto D solo vendió fuera del rango: no debe aparecer
    ids = [item["id"] for item in json.loads(response.content)]
    assert productos_con_ventas_en_octubre["producto_d"].id not in ids
