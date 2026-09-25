 # tests/infrastructure/http/test_registrar_vendedor_view.py
"""
Tests de la vista RegistrarVendedor (APIView).

Esta vista SÍ toca Django: usa el ORM (vía DjangoUsuarioRepository) y
el request/response de DRF. Por eso @pytest.mark.django_db.

Estrategia:
- Crear un admin real en la BD antes de cada test (necesario porque el
  caso de uso valida que el admin exista y sea admin).
- Usar el test client de DRF para simular requests HTTP.
- Verificar el status code y el shape del body, no los mensajes exactos
  (esos dependen de i18n y podrían cambiar).
"""

import pytest
from rest_framework.test import APIClient

from apps.usuarios.models import AdministradorORM, VendedorORM  # ajustá el import
from core.domain.usuario.usuario import Usuario, EstadoUsuario
from core.domain.usuario.value_objects import (
    Email,
    NombreUsuario,
    Password,
    PasswordHash,
    RolUser,
    UsuarioId,
)
from infrastructure.django.repositories.usuario_repository import DjangoUsuarioRepository


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def admin_en_bd() -> UsuarioId:
    """
    Crea un admin real en la BD y devuelve su UsuarioId.

    Necesario porque CrearVendedor exige que el admin_id referencie a un
    admin real. Sin esto, el caso de uso siempre lanza AdminNoEncontradoException.
    """
    repo = DjangoUsuarioRepository()
    admin = Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Admin Test"),
        email=Email("admin@test.com"),
        password_hash=PasswordHash("$2b$12$hash"),
        rol=RolUser(RolUser.ADMINISTRADOR),
        activo=EstadoUsuario.activo(),
    )
    repo.guardar_administrador(admin)
    return admin.id


def _payload_valido(admin_id: str) -> dict:
    return {
        "nombre": "Vendedor Test",
        "email": "vendedor@test.com",
        "password_plana": "Abc123!x",
        "admin_id": str(admin_id),
    }


URL = "/api/usuarios/registrar-vendedor/"   # ← ajustá a tu ruta real


# =========================================================================
# GET: endpoint de salud
# =========================================================================

@pytest.mark.django_db
def test_get_devuelve_ok(api_client):
    """
    Si falla: el endpoint de salud no responde.
    """
    response = api_client.get(URL)
    assert response.status_code == 200
    assert response.data == {"status": "OK"}


# =========================================================================
# POST: caso feliz
# =========================================================================

@pytest.mark.django_db
def test_post_crea_vendedor_con_datos_validos(api_client, admin_en_bd):
    """
    Si falla: no se puede registrar un vendedor con datos correctos.

    Verifica:
    - Status 201.
    - Que el vendedor quedó en la BD.
    - Que el vendedor está asociado al admin correcto.
    """
    response = api_client.post(
        URL,
        data=_payload_valido(admin_en_bd),
        format="json",
    )

    assert response.status_code == 201
    assert response.data == {"mensaje": "OK"}

    # Verificamos persistencia
    vendedor_orm = VendedorORM.objects.filter(email="vendedor@test.com").first()
    assert vendedor_orm is not None
    assert vendedor_orm.admin.uuid == admin_en_bd.valor


@pytest.mark.django_db
def test_post_crea_vendedor_con_rol_vendedor(api_client, admin_en_bd):
    """
    Si falla: el vendedor queda registrado con rol equivocado.
    """
    api_client.post(URL, data=_payload_valido(admin_en_bd), format="json")

    vendedor_orm = VendedorORM.objects.get(email="vendedor@test.com")
    # El modelo VendedorORM siempre implica rol vendedor; no hay campo rol
    # en la BD. La verificación real es que esté en la tabla correcta.
    assert vendedor_orm is not None


# =========================================================================
# POST: campos faltantes
# =========================================================================

@pytest.mark.parametrize(
    "campo_faltante",
    ["nombre", "email", "password_plana", "admin_id"],
)
@pytest.mark.django_db
def test_post_falla_si_falta_un_campo(
    api_client, admin_en_bd, campo_faltante
):
    """
    Si falla: la vista acepta requests sin algún campo obligatorio.
    """
    payload = _payload_valido(admin_en_bd)
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
        ("admin_id", ""),
        ("nombre", None),
        ("admin_id", None),
    ],
)
@pytest.mark.django_db
def test_post_falla_si_campo_viene_vacio(
    api_client, admin_en_bd, campo, valor_vacio
):
    """
    Si falla: la vista acepta campos vacíos o None como válidos.
    """
    payload = _payload_valido(admin_en_bd)
    payload[campo] = valor_vacio

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code == 400
    assert campo in response.data["campos_faltantes"]


# =========================================================================
# POST: admin_id con formato inválido
# =========================================================================

@pytest.mark.parametrize(
    "admin_id_invalido",
    ["no-es-uuid", "12345", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "   "],
)
@pytest.mark.django_db
def test_post_falla_si_admin_id_tiene_formato_invalido(
    api_client, admin_id_invalido
):
    """
    Si falla: se acepta un admin_id que no es un UUID válido.

    La vista atrapa UsuarioIdInvalidoException y responde 400 con error_campo.
    """
    payload = {
        "nombre": "Vendedor",
        "email": "v@test.com",
        "password_plana": "Abc123!x",
        "admin_id": admin_id_invalido,
    }

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code == 400
    assert "error_campo" in response.data
    assert "admin_id" in response.data["error_campo"]


# =========================================================================
# POST: admin no existe
# =========================================================================

@pytest.mark.django_db
def test_post_falla_si_admin_no_existe(api_client):
    """
    Si falla: se puede crear un vendedor con un admin_id que no existe.

    La vista delega en CrearVendedor, que lanza AdminNoEncontradoException.
    """
    admin_id_inexistente = str(UsuarioId.generar())

    payload = {
        "nombre": "Vendedor",
        "email": "v@test.com",
        "password_plana": "Abc123!x",
        "admin_id": admin_id_inexistente,
    }

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code >= 400
    # No validamos el código exacto (depende de i18n).
    # Solo que sea un error de dominio serializado.
    assert isinstance(response.data, dict)


# =========================================================================
# POST: email duplicado
# =========================================================================

@pytest.mark.django_db
def test_post_falla_si_email_ya_registrado(api_client, admin_en_bd):
    """
    Si falla: se permiten dos vendedores con el mismo email.
    """
    payload = _payload_valido(admin_en_bd)

    # Primer alta: OK
    response1 = api_client.post(URL, data=payload, format="json")
    assert response1.status_code == 201

    # Segundo alta con el mismo email: debe fallar
    response2 = api_client.post(URL, data=payload, format="json")
    assert response2.status_code >= 400


# =========================================================================
# POST: usuario logueado como vendedor (no admin)
# =========================================================================

@pytest.mark.django_db
def test_post_falla_si_el_usuario_objetivo_no_es_admin(
    api_client,
):
    """
    Si falla: se puede asociar un vendedor a otro vendedor.

    Creamos un vendedor (asociado a un admin real), y después intentamos
    usar el ID del vendedor como admin_id. El caso de uso debe rechazarlo.
    """
    # Creamos un admin
    admin = Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Admin"),
        email=Email("admin@test.com"),
        password_hash=PasswordHash("$2b$12$hash"),
        rol=RolUser(RolUser.ADMINISTRADOR),
        activo=EstadoUsuario.activo(),
    )
    DjangoUsuarioRepository().guardar_administrador(admin)

    # Creamos un vendedor asociado a ese admin
    vendedor = Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Vendedor"),
        email=Email("v1@test.com"),
        password_hash=PasswordHash("$2b$12$hash2"),
        rol=RolUser(RolUser.VENDEDOR),
        activo=EstadoUsuario.activo(),
    )
    DjangoUsuarioRepository().guardar_vendedor_con_admin(vendedor, admin.id)

    # Ahora intentamos crear otro vendedor usando el ID del vendedor
    # existente como si fuera admin_id
    payload = {
        "nombre": "Otro Vendedor",
        "email": "v2@test.com",
        "password_plana": "Abc123!x",
        "admin_id": str(vendedor.id.valor),
    }

    response = api_client.post(URL, data=payload, format="json")

    assert response.status_code >= 400
