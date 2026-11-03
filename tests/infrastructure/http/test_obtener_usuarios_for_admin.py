# tests/infrastructure/http/test_obtener_usuarios_for_admin.py
"""
Test de integración de:
    GET /api/usuarios/get_user/admin/<admin_id>/vendedores/

No usa mocks: crea administradores y vendedores reales en la BD de test,
autentica con un JWT real y consulta el endpoint.

El "JSON de entrada" de un GET no es un body: es la URL con el admin_id.
Lo que se valida es el JSON de salida (lista de vendedores del admin).
"""

import json

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.usuarios.models import AdministradorORM, VendedorORM


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def admin_dueno() -> AdministradorORM:
    """Admin cuyos vendedores queremos listar."""
    return AdministradorORM.objects.create(
        username="admin_dueno",
        email="admin_dueno@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )


@pytest.fixture
def otro_admin() -> AdministradorORM:
    """Admin distinto, para comprobar que sus vendedores NO aparecen."""
    return AdministradorORM.objects.create(
        username="admin_ajeno",
        email="admin_ajeno@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )


@pytest.fixture
def vendedores_de_prueba(admin_dueno, otro_admin):
    """
    Dos vendedores del admin dueño y uno de otro admin.
    """
    VendedorORM.objects.create(
        username="vendedor_ana",
        email="ana@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
        admin=admin_dueno,
    )
    VendedorORM.objects.create(
        username="vendedor_luis",
        email="luis@test.com",
        password=make_password("clave-de-test"),
        activo="inactivo",
        admin=admin_dueno,
    )
    VendedorORM.objects.create(
        username="vendedor_ajeno",
        email="ajeno@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
        admin=otro_admin,
    )


@pytest.fixture
def api_client(admin_dueno) -> APIClient:
    """Cliente autenticado con un JWT real."""
    client = APIClient()
    token = AccessToken.for_user(admin_dueno)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# =========================================================================
# GET: vendedores por administrador
# =========================================================================

@pytest.mark.django_db
def test_get_devuelve_solo_los_vendedores_del_admin(
    api_client,
    admin_dueno,
    vendedores_de_prueba,
):
    """
    Si falla: el endpoint no filtra por admin o devuelve datos incompletos.
    """

    # ------------------------------------------------------------------
    # "Entrada" del GET: la URL con el UUID del admin
    # ------------------------------------------------------------------
    url_del_endpoint = (
        f"/api/usuarios/get_user/admin/{admin_dueno.uuid}/vendedores/"
    )

    # ------------------------------------------------------------------
    # Llamada real al endpoint
    # ------------------------------------------------------------------
    response = api_client.get(url_del_endpoint)

    # ------------------------------------------------------------------
    # JSON que ESPERAMOS recibir
    # (fecha_creacion la genera la BD, se valida aparte)
    # ------------------------------------------------------------------
    respuesta_esperada = [
        {
            "uuid": str(VendedorORM.objects.get(username="vendedor_ana").uuid),
            "username": "vendedor_ana",
            "email": "ana@test.com",
            "activo": "activo",
            "admin": str(admin_dueno.uuid),
        },
        {
            "uuid": str(VendedorORM.objects.get(username="vendedor_luis").uuid),
            "username": "vendedor_luis",
            "email": "luis@test.com",
            "activo": "inactivo",
            "admin": str(admin_dueno.uuid),
        },
    ]

    assert response.status_code == 200

    # JSON tal cual lo recibe el cliente
    json_recibido = json.loads(response.content)
    recibidos = {item["username"]: item for item in json_recibido}

    # Solo deben venir los 2 vendedores del admin dueño.
    assert set(recibidos) == {"vendedor_ana", "vendedor_luis"}
    assert "vendedor_ajeno" not in recibidos

    for esperado in respuesta_esperada:
        item = recibidos[esperado["username"]]

        # fecha_creacion existe y tiene formato ISO, pero no comparamos
        # el valor exacto porque lo genera la BD.
        assert "T" in item.pop("fecha_creacion")

        assert item == esperado

    # Verificación directa en la BD
    assert VendedorORM.objects.filter(admin=admin_dueno).count() == 2
