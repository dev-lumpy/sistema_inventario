# tests/infrastructure/http/test_producto_create.py
"""
Test de integración de:
    POST /api/inventario/productos/

Verifica que el administrador se tome de la sesión autenticada y no del
cuerpo de la petición.
"""

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.inventario.models import Categoria, Producto
from apps.usuarios.models import AdministradorORM, VendedorORM


URL_PRODUCTOS = "/api/inventario/productos/"


@pytest.fixture
def categoria(db) -> Categoria:
    return Categoria.objects.create(nombre="Categoría Test")


@pytest.fixture
def admin(db) -> AdministradorORM:
    return AdministradorORM.objects.create(
        username="admin_producto",
        email="admin_producto@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )


def _cliente_autenticado(usuario):
    client = APIClient()
    token = AccessToken.for_user(usuario)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


def _payload(categoria: Categoria) -> dict:
    return {
        "nombre": "Producto Nuevo",
        "categoria": categoria.id,
        "precio_unitario": "1500.00",
        "stock_minimo": 2,
        "cantidad_inicial": 5,
    }


@pytest.mark.django_db
def test_crea_producto_y_asigna_el_admin_autenticado(admin, categoria):
    client = _cliente_autenticado(admin)

    response = client.post(URL_PRODUCTOS, data=_payload(categoria), format="json")

    assert response.status_code == 201
    producto = Producto.objects.get(nombre="Producto Nuevo")
    assert producto.administrador_id == admin.pk
    assert str(response.data["administrador"]) == str(admin.pk)


@pytest.mark.django_db
def test_vendedor_no_puede_crear_producto(admin, categoria):
    vendedor = VendedorORM.objects.create(
        username="vendedor_producto",
        email="vendedor_producto@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
        admin=admin,
    )
    client = _cliente_autenticado(vendedor)

    response = client.post(URL_PRODUCTOS, data=_payload(categoria), format="json")

    assert response.status_code == 400
    assert "administrador" in response.data
    assert not Producto.objects.exists()
