# tests/infrastructure/http/test_movimiento_stock.py
"""
Test de integración del endpoint de salida de stock (venta).

No usa mocks: levanta Django, crea datos reales en la BD de test,
hace un POST real al endpoint y verifica que el movimiento se registre.

Ruta probada:
    POST /api/inventario/movimiento/salida/
"""

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.inventario.models import Categoria, MovimientoStock, Producto
from apps.usuarios.models import AdministradorORM


URL_REGISTRAR_SALIDA = "/api/inventario/movimiento/salida/"


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def administrador_en_bd() -> AdministradorORM:
    """Usuario real en la BD, necesario porque el endpoint exige autenticación."""
    return AdministradorORM.objects.create(
        username="admin_test",
        email="admin_test@example.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )


@pytest.fixture
def api_client(administrador_en_bd) -> APIClient:
    """
    Cliente HTTP autenticado con un JWT real (mismo camino que usa la app).
    """
    client = APIClient()
    token = AccessToken.for_user(administrador_en_bd)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def producto_con_stock() -> Producto:
    """
    Crea un producto real con 10 unidades de stock.

    El stock se calcula desde los movimientos, así que creamos un
    movimiento de entrada inicial de 10 unidades.
    """
    categoria = Categoria.objects.create(nombre="Lubricantes Test")

    producto = Producto.objects.create(
        nombre="Aceite Test 5L",
        categoria=categoria,
        precio_unitario="18500.00",
        stock_minimo=3,
        activo=True,
    )

    MovimientoStock.objects.create(
        producto=producto,
        tipo=MovimientoStock.TIPO_ENTRADA,
        motivo=MovimientoStock.MOTIVO_INICIAL,
        cantidad=10,
        detalle="Stock inicial del test",
    )

    return producto


# =========================================================================
# POST: registrar una venta (salida de stock)
# =========================================================================

@pytest.mark.django_db
def test_post_registra_una_venta_y_descuenta_stock(api_client, producto_con_stock):
    """
    Si falla: el endpoint no registra la salida o no descuenta el stock.
    """

    # ------------------------------------------------------------------
    # JSON que ENVIAMOS al endpoint
    # ------------------------------------------------------------------
    payload_que_enviamos = {
        "producto": producto_con_stock.id,
        "cantidad": 2,
        "canal_venta": "whatsapp",
    }

    # ------------------------------------------------------------------
    # Llamada real al endpoint
    # ------------------------------------------------------------------
    response = api_client.post(
        URL_REGISTRAR_SALIDA,
        data=payload_que_enviamos,
        format="json",
    )

    # ------------------------------------------------------------------
    # JSON que ESPERAMOS recibir
    # (movimiento_id se separa porque lo genera la BD)
    # ------------------------------------------------------------------
    respuesta_esperada = {
        "mensaje": "Venta registrada correctamente.",
        "producto_id": producto_con_stock.id,
        "producto": "Aceite Test 5L",
        "cantidad": 2,
        "canal_venta": "whatsapp",
        "nuevo_stock": 8,
    }

    respuesta_recibida = dict(response.data)
    movimiento_id = respuesta_recibida.pop("movimiento_id")

    assert response.status_code == 201
    assert isinstance(movimiento_id, int)
    assert respuesta_recibida == respuesta_esperada

    # ------------------------------------------------------------------
    # Verificamos que realmente se guardó en la BD
    # ------------------------------------------------------------------
    movimiento = MovimientoStock.objects.get(id=movimiento_id)
    assert movimiento.tipo == MovimientoStock.TIPO_SALIDA
    assert movimiento.motivo == MovimientoStock.MOTIVO_VENTA
    assert movimiento.canal_venta == "whatsapp"
    assert movimiento.cantidad == 2
    assert movimiento.producto_id == producto_con_stock.id
    assert movimiento.proveedor_id is None

    producto_con_stock.refresh_from_db()
    assert producto_con_stock.stock_actual == 8

    # Entrada inicial + venta = 2 movimientos del producto
    assert MovimientoStock.objects.filter(producto=producto_con_stock).count() == 2
