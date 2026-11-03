# tests/infrastructure/http/test_productos_mas_vendidos.py
"""
Test de integración de:
    GET /api/inventario/productos/mas-vendidos/

No usa mocks: crea productos y movimientos reales en la BD de test,
autentica con un JWT real y consulta el endpoint.
"""

import json

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.inventario.models import Categoria, MovimientoStock, Producto
from apps.usuarios.models import AdministradorORM


URL_MAS_VENDIDOS = "/api/inventario/productos/mas-vendidos/"


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def api_client() -> APIClient:
    admin = AdministradorORM.objects.create(
        username="admin_mas_vendidos",
        email="admin_mas_vendidos@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )

    client = APIClient()
    token = AccessToken.for_user(admin)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def productos_con_ventas(administrador):
    categoria = Categoria.objects.create(nombre="Frenos Test")

    def crear_producto(nombre: str) -> Producto:
        return Producto.objects.create(
            nombre=nombre,
            categoria=categoria,
            precio_unitario="1000.00",
            stock_minimo=1,
            activo=True,
            administrador=administrador,
        )

    def entrada(producto: Producto, cantidad: int) -> None:
        MovimientoStock.objects.create(
            producto=producto,
            tipo=MovimientoStock.TIPO_ENTRADA,
            motivo=MovimientoStock.MOTIVO_INICIAL,
            cantidad=cantidad,
            detalle="Stock inicial del test",
        )

    def salida(producto: Producto, cantidad: int, motivo: str = "venta", canal=None) -> None:
        MovimientoStock.objects.create(
            producto=producto,
            tipo=MovimientoStock.TIPO_SALIDA,
            motivo=motivo,
            cantidad=cantidad,
            canal_venta=canal,
            detalle=f"Movimiento {motivo} del test",
        )

    producto_a = crear_producto("Producto A")
    producto_b = crear_producto("Producto B")
    producto_c = crear_producto("Producto C")
    producto_d = crear_producto("Producto D")

    for producto, stock in (
        (producto_a, 200),
        (producto_b, 100),
        (producto_c, 50),
        (producto_d, 10),
    ):
        entrada(producto, stock)

    # Producto A: 70 + 50 = 120 vendidos
    salida(producto_a, 70, canal="whatsapp")
    salida(producto_a, 50, canal="presencial")

    # Producto B: 80 vendidos
    salida(producto_b, 80, canal="instagram")

    # Producto C: 35 vendidos
    salida(producto_c, 35, canal="facebook")

    # Ruido: una merma NO debe contar como venta
    salida(producto_a, 5, motivo=MovimientoStock.MOTIVO_MERMA)

    # Producto D no tiene ventas: no debe aparecer

    return {
        "producto_a": producto_a,
        "producto_b": producto_b,
        "producto_c": producto_c,
        "producto_d": producto_d,
    }


# =========================================================================
# GET: ranking de productos más vendidos
# =========================================================================

@pytest.mark.django_db
def test_get_devuelve_el_ranking_de_mas_vendidos(api_client, productos_con_ventas):
    """
    Si falla: el endpoint no ordena por cantidad, no suma bien o cuenta
    movimientos que no son ventas.
    """

    response = api_client.get(URL_MAS_VENDIDOS)

    # ------------------------------------------------------------------
    # JSON que ESPERAMOS recibir
    # ------------------------------------------------------------------
    respuesta_esperada = [
        {"nombre": "Producto A", "cantidad_vendida": 120},
        {"nombre": "Producto B", "cantidad_vendida": 80},
        {"nombre": "Producto C", "cantidad_vendida": 35},
    ]

    assert response.status_code == 200
    assert json.loads(response.content) == respuesta_esperada

    # Producto D (sin ventas) no aparece
    nombres = [item["nombre"] for item in json.loads(response.content)]
    assert "Producto D" not in nombres
