"""Tests de GET /api/inventario/history_movimientos/<limite>/.

Objetivo: comprobar que la URL devuelve los últimos ``limite`` registros
reales de la tabla ``MovimientoStock``, ordenados del más reciente al más
antiguo, con el contrato que expone ``MovimientoHistorialMovimientoSerializer``.
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.inventario.models import MovimientoStock
from tests.factories import (
    AdministradorFactory,
    CategoriaFactory,
    MovimientoStockFactory,
    ProductoFactory,
    ProveedorFactory,
)

URL = "/api/inventario/history_movimientos"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return AdministradorFactory()


@pytest.fixture
def client_auth(api_client, admin):
    api_client.force_authenticate(user=admin)
    return api_client


def _movimiento(producto, fecha, **kwargs):
    """Crea un movimiento y le fija una fecha histórica explícita."""
    movimiento = MovimientoStockFactory(producto=producto, **kwargs)
    # fecha usa auto_now_add, por eso se fija con update.
    MovimientoStock.objects.filter(pk=movimiento.pk).update(fecha=fecha)
    return movimiento


def _crear_movimientos(admin, cantidad):
    categoria = CategoriaFactory(nombre="Frenos")
    producto = ProductoFactory(administrador=admin, categoria=categoria)
    base = timezone.now() - timedelta(days=30)
    return [
        _movimiento(producto, fecha=base + timedelta(minutes=i))
        for i in range(cantidad)
    ]


@pytest.mark.django_db
def test_devuelve_los_ultimos_x_movimientos(client_auth, admin):
    """Con 12 movimientos y limite=5 devuelve los 5 más recientes, en orden."""
    movimientos = _crear_movimientos(admin, 12)

    response = client_auth.get(f"{URL}/5/")

    assert response.status_code == 200
    ids = [item["id"] for item in response.data]
    assert ids == [movimiento.id for movimiento in reversed(movimientos)][:5]
    assert len(ids) == 5


@pytest.mark.django_db
def test_limite_cero_devuelve_lista_vacia(client_auth, admin):
    """Con limite=0 no devuelve ningún registro."""
    _crear_movimientos(admin, 3)

    response = client_auth.get(f"{URL}/0/")

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_limite_mayor_a_la_cantidad_devuelve_todos(client_auth, admin):
    """Si el límite supera la cantidad de filas, devuelve todas."""
    movimientos = _crear_movimientos(admin, 3)

    response = client_auth.get(f"{URL}/50/")

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [
        movimiento.id for movimiento in reversed(movimientos)
    ]


@pytest.mark.django_db
def test_techo_maximo_de_cien_registros(client_auth, admin):
    """Aunque la URL pida 999, la vista recorta a 100 registros."""
    movimientos = _crear_movimientos(admin, 105)

    response = client_auth.get(f"{URL}/999/")

    assert response.status_code == 200
    assert len(response.data) == 100
    assert [item["id"] for item in response.data] == [
        movimiento.id for movimiento in reversed(movimientos)
    ][:100]


@pytest.mark.django_db
def test_sin_slash_final_tambien_funciona(client_auth, admin):
    """La ruta acepta la URL sin slash final."""
    _crear_movimientos(admin, 2)

    assert client_auth.get(f"{URL}/2").status_code == 200


@pytest.mark.django_db
def test_devuelve_datos_reales_de_movimientostock(client_auth, admin):
    """Verifica que los registros provienen de MovimientoStock y su shape."""
    categoria = CategoriaFactory(nombre="Lubricantes")
    producto = ProductoFactory(administrador=admin, categoria=categoria)
    proveedor = ProveedorFactory(nombre="Proveedor Demo")
    fecha = timezone.now() - timedelta(days=2)

    compra = _movimiento(
        producto,
        fecha,
        tipo=MovimientoStock.TIPO_ENTRADA,
        motivo=MovimientoStock.MOTIVO_COMPRA,
        cantidad=7,
        proveedor=proveedor,
        detalle="Factura A-1",
    )
    _movimiento(
        producto,
        fecha + timedelta(minutes=1),
        tipo=MovimientoStock.TIPO_SALIDA,
        motivo=MovimientoStock.MOTIVO_VENTA,
        cantidad=2,
        canal_venta="whatsapp",
    )

    response = client_auth.get(f"{URL}/10/")

    assert response.status_code == 200
    items = {item["id"]: item for item in response.data}
    assert set(items) == set(MovimientoStock.objects.values_list("id", flat=True))

    item = items[compra.id]
    assert set(item) == {"id", "categoria", "cantidad", "proveedor", "fecha"}
    assert item["categoria"] == "Lubricantes"
    assert item["cantidad"] == 7
    assert item["proveedor"] == "Proveedor Demo"
    assert item["fecha"] == fecha.strftime("%Y-%m-%dT%H:%M:%S")

    venta = next(
        item for item in response.data
        if item["id"] != compra.id
    )
    assert venta["proveedor"] == "—"


@pytest.mark.django_db
def test_requiere_autenticacion(api_client):
    """La vista exige un usuario autenticado."""
    assert api_client.get(f"{URL}/5/").status_code == 401
