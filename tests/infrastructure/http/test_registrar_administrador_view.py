# tests/infrastructure/http/test_registrar_administrador_view.py
"""
Tests de la vista RegistrarAdministrador (APIView).

Esta vista toca Django (ORM vía DjangoUsuarioRepository) y DRF.
Por eso @pytest.mark.django_db.

Diferencias con RegistrarVendedor:
- No hay admin_id, así que no hay tests de "admin no existe" ni "no es admin".
- El caso de uso es CrearAdministrador, que devuelve un UsuarioId.
"""

import pytest
from rest_framework.test import APIClient

from apps.usuarios.models import AdministradorORM


URL = "/api/usuarios/registrar-admin/"   # ← ajustá a tu ruta real


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def _payload_valido() -> dict:
    return {
        "nombre": "Admin Test",
        "email": "admin@test.com",
        "password_plana": "Abc123!x",
    }


# =========================================================================
# Caso feliz
# =========================================================================

@pytest.mark.django_db
def test_post_crea_administrador_con_datos_validos(api_client):
    """
    Si falla: no se puede registrar un administrador con datos correctos.
    """
    response = api_client.post(URL, data=_payload_valido(), format="json")

    assert response.status_code == 201
    assert response.data["mensaje"] == "OK"
    assert "id" in response.data

    # Verificamos persistencia
    admin_orm = AdministradorORM.objects.filter(email="admin@test.com").first()
    assert admin_orm is not None
    assert admin_orm.username == "Admin Test"


@pytest.mark.django_db
def test_post_devuelve_el_id_del_administrador_creado(api_client):
    """
    Si falla: la vista no devuelve el id del admin creado.

    Es útil para que el cliente pueda redirigir o hacer follow-up.
    """
    response = api_client.post(URL, data=_payload_valido(), format="json")

    assert response.status_code == 201
    admin_id = response.data["id"]

    # Verificamos que ese UUID existe en la BD
    assert AdministradorORM.objects.filter(uuid=admin_id).exists()


@pytest.mark.django_db
def test_post_guarda_la_password_hasheada_no_plana(api_client):
    """
    Si falla: se guarda la contraseña en texto plano (bug de seguridad).
    """
    api_client.post(URL, data=_payload_valido(), format="json")

    admin_orm = AdministradorORM.objects.get(email="admin@test.com")
    assert admin_orm.password != "Abc123!x"
    assert "Abc123!x" not in admin_orm.password


@pytest.mark.django_db
def test_post_normaliza_el_email(api_client):
    """
    Si falla: el email se guarda con espacios o mayúsculas.
    """
    payload = _payload_valido()
    payload["email"] = "  ADMIN@Example.COM  "

    api_client.post(URL, data=payload, format="json")

    admin_orm = AdministradorORM.objects.get(username="Admin Test")
    assert admin_orm.email == "admin@example.com"


# =========================================================================
# Campos faltantes
# =========================================================================

@pytest.mark.parametrize(
    "campo_faltante",
    ["nombre", "email", "password_plana"],
)
@pytest.mark.django_db
def test_post_falla_si_falta_un_campo(api_client, campo_faltante):
    """
    Si falla: la vista acepta requests sin algún campo obligatorio.
    """
    payload = _payload_valido()
    del payload[campo_faltante]

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code == 400
    assert "campos_faltantes" in response.data
    assert campo_faltante in response.data["campos_faltantes"]


@pytest.mark.parametrize(
    "campo,valor_vacio",
    [
        ("nombre", ""),
        ("email", ""),
        ("password_plana", ""),
        ("nombre", None),
        ("email", None),
        ("password_plana", None),
    ],
)
@pytest.mark.django_db
def test_post_falla_si_campo_viene_vacio(api_client, campo, valor_vacio):
    """
    Si falla: la vista acepta campos vacíos o None como válidos.
    """
    payload = _payload_valido()
    payload[campo] = valor_vacio

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code == 400
    assert campo in response.data["campos_faltantes"]


# =========================================================================
# Email duplicado
# =========================================================================

@pytest.mark.django_db
def test_post_falla_si_email_ya_registrado(api_client):
    """
    Si falla: se permiten dos administradores con el mismo email.
    """
    payload = _payload_valido()

    # Primer alta: OK
    response1 = api_client.post(URL, data=payload, format="json")
    assert response1.status_code == 201

    # Segundo alta con el mismo email: debe fallar
    response2 = api_client.post(URL, data=payload, format="json")
    assert response2.status_code >= 400


# =========================================================================
# Contraseña inválida (validación del VO Password)
# =========================================================================

@pytest.mark.parametrize(
    "password_invalida",
    [
        "corta",            # menos de 8 caracteres
        "sinmayuscula1!",   # sin mayúscula
        "SINMINUSCULA1!",   # sin minúscula
        "SinDigito!",       # sin dígito
        "SinEspecial1",     # sin especial
        "Abc 123!x",        # con espacio interno
        "aaaa1!xyz",        # 4 aes minúsculas (dispara repetidos)
        "AAAA1!xyz",        # 4 A mayúsculas (dispara repetidos)
    ],
)
@pytest.mark.django_db
def test_post_falla_si_password_no_cumple_las_reglas(api_client, password_invalida):
    """
    Si falla: se crea un admin con una contraseña que viola las reglas.

    El VO Password valida las reglas; el caso de uso debería propagar
    la excepción y la vista debería devolver 400.
    """
    payload = _payload_valido()
    payload["password_plana"] = password_invalida

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code >= 400


# =========================================================================
# Nombre inválido
# =========================================================================

@pytest.mark.parametrize(
    "nombre_invalido",
    ["", " ", "A"],   # vacío, solo espacios, demasiado corto
)
@pytest.mark.django_db
def test_post_falla_si_nombre_no_cumple_las_reglas(api_client, nombre_invalido):
    """
    Si falla: se crea un admin con un nombre inválido.
    """
    payload = _payload_valido()
    payload["nombre"] = nombre_invalido

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code >= 400


# =========================================================================
# Email con formato inválido
# =========================================================================

@pytest.mark.parametrize(
    "email_invalido",
    ["sin-arroba", "sin@dominio", "@sin-usuario.com", "usuario@"],
)
@pytest.mark.django_db
def test_post_falla_si_email_tiene_formato_invalido(api_client, email_invalido):
    """
    Si falla: se acepta un email con formato inválido.
    """
    payload = _payload_valido()
    payload["email"] = email_invalido

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code >= 400
