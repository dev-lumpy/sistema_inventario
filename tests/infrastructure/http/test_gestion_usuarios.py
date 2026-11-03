# tests/infrastructure/http/test_gestion_usuarios.py
"""
Tests de integración de:
    PATCH  /api/usuarios/api/<uuid>/
    DELETE /api/usuarios/api/<uuid>/

No usan mocks: crean un administrador y vendedores reales en la BD de test,
autentican con un JWT real y llaman al endpoint.
"""

import json

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.usuarios.models import AdministradorORM, UsuarioORM, VendedorORM


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def admin_en_bd() -> AdministradorORM:
    return AdministradorORM.objects.create(
        username="admin_gestion",
        email="admin_gestion@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )


@pytest.fixture
def vendedor_en_bd(admin_en_bd) -> VendedorORM:
    return VendedorORM.objects.create(
        username="vendedor_original",
        email="original@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
        admin=admin_en_bd,
    )


@pytest.fixture
def api_client(admin_en_bd) -> APIClient:
    client = APIClient()
    token = AccessToken.for_user(admin_en_bd)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# =========================================================================
# PATCH: actualizar vendedor
# =========================================================================

@pytest.mark.django_db
def test_patch_actualiza_los_datos_del_vendedor(api_client, vendedor_en_bd, admin_en_bd):
    """
    Si falla: el endpoint no actualiza username/email/activo.
    """

    url_del_endpoint = f"/api/usuarios/api/{vendedor_en_bd.uuid}/"

    # ------------------------------------------------------------------
    # JSON que ENVIAMOS
    # ------------------------------------------------------------------
    cuerpo_que_enviamos = {
        "username": "vendedor_editado",
        "email": "editado@test.com",
        "activo": "inactivo",
    }

    response = api_client.patch(
        url_del_endpoint,
        data=cuerpo_que_enviamos,
        format="json",
    )

    # ------------------------------------------------------------------
    # JSON que ESPERAMOS recibir
    # ------------------------------------------------------------------
    respuesta_esperada = {
        "uuid": str(vendedor_en_bd.uuid),
        "username": "vendedor_editado",
        "email": "editado@test.com",
        "activo": "inactivo",
    }

    assert response.status_code == 200

    json_recibido = json.loads(response.content)
    json_recibido.pop("fecha_creacion")

    assert json_recibido == respuesta_esperada

    # Verificación directa en la BD
    vendedor_actualizado = VendedorORM.objects.get(uuid=vendedor_en_bd.uuid)
    assert vendedor_actualizado.username == "vendedor_editado"
    assert vendedor_actualizado.email == "editado@test.com"
    assert vendedor_actualizado.activo == "inactivo"
    assert vendedor_actualizado.admin_id == admin_en_bd.uuid


# =========================================================================
# DELETE: eliminar vendedor
# =========================================================================

@pytest.mark.django_db
def test_delete_elimina_al_vendedor(api_client, vendedor_en_bd, admin_en_bd):
    """
    Si falla: el endpoint no elimina al vendedor (ni su fila padre).
    """

    url_del_endpoint = f"/api/usuarios/api/{vendedor_en_bd.uuid}/"

    # Un segundo vendedor para comprobar que no se borra de más
    otro_vendedor = VendedorORM.objects.create(
        username="vendedor_queda",
        email="queda@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
        admin=admin_en_bd,
    )

    response = api_client.delete(url_del_endpoint)

    # DELETE no devuelve body: 204 No Content
    assert response.status_code == 204
    assert response.content == b""

    assert not VendedorORM.objects.filter(uuid=vendedor_en_bd.uuid).exists()
    assert not UsuarioORM.objects.filter(uuid=vendedor_en_bd.uuid).exists()

    # El otro vendedor sigue existiendo
    assert VendedorORM.objects.filter(uuid=otro_vendedor.uuid).exists()
