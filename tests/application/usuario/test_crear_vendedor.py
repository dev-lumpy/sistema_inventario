 # tests/application/usuario/test_crear_vendedor.py
"""
Tests del caso de uso CrearVendedor.

Mockeamos repo y hasher. El objetivo es testear la orquestación:
validar email → validar admin → validar rol → hashear → guardar.
"""

from unittest.mock import Mock

import pytest

from core.application.ports.password_hasher import PasswordHasher
from core.application.usuario.crear_vendedor import CrearVendedor
from core.domain.usuario.exceptions import (
    AdminNoEncontradoException,
    EmailYaRegistradoException,
    UsuarioNoEsAdminException,
)
from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import (
    Email,
    PasswordHash,
    RolUser,
    UsuarioId,
    Password
)


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def repo() -> Mock:
    """Mock del UsuarioRepository. No toca base de datos."""
    return Mock(spec=UsuarioRepository)


@pytest.fixture
def hasher() -> Mock:
    """Mock del PasswordHasher. No hashea de verdad."""
    mock = Mock(spec=PasswordHasher)
    mock.hashear.return_value = PasswordHash("$2b$12$fakehash")

    return mock


@pytest.fixture
def caso_uso(repo: Mock, hasher: Mock) -> CrearVendedor:
    """Instancia real del caso de uso con colaboradores mockeados."""
    return CrearVendedor(usuario_repo=repo, password_hasher=hasher)


@pytest.fixture
def admin_existente() -> Mock:
    """
    Mock que se hace pasar por un Usuario administrador válido.

    Configuramos es_administrador() para que devuelva True porque el
    caso de uso lo llama como método. Si en tu Usuario es una @property,
    esta línea tiene que cambiar (ver nota abajo).
    """
    admin = Mock(spec=Usuario)
    admin.es_administrador.return_value = True
    return admin


@pytest.fixture
def vendedor_existente() -> Mock:
    """Mock de un Usuario que NO es administrador."""
    vendedor = Mock(spec=Usuario)
    vendedor.es_administrador.return_value = False
    return vendedor


@pytest.fixture
def admin_id() -> UsuarioId:
    return UsuarioId.generar()


# =========================================================================
# Caso feliz
# =========================================================================

def test_crear_vendedor_devuelve_usuario_id(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: el caso de uso no completa el flujo ni devuelve un ID.

    Configuramos el repo para el camino feliz: email libre + admin válido.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = admin_existente

    resultado = caso_uso.ejecutar(
        nombre="Vendedor Test",
        email="vendedor@example.com",
        password_plana="Abc123!x",
        admin_id=admin_id,
    )

    assert isinstance(resultado, UsuarioId)


def test_crear_vendedor_consulta_email_y_admin(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: no se valida el email o no se valida que el admin exista.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = admin_existente

    caso_uso.ejecutar(
        nombre="Vendedor",
        email="v@example.com",
        password_plana="Abc123!x",
        admin_id=admin_id,
    )

    repo.obtener_por_email.assert_called_once()
    repo.obtener_por_id.assert_called_once_with(admin_id)


def test_crear_vendedor_guarda_con_rol_vendedor(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se crea al usuario como administrador por error.

    Bug clásico: copiar/pegar de CrearAdministrador y olvidar cambiar el rol.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = admin_existente

    caso_uso.ejecutar(
        nombre="Vendedor",
        email="v@example.com",
        password_plana="Abc123!x",
        admin_id=admin_id,
    )

    repo.guardar_vendedor_con_admin.assert_called_once()
    vendedor_guardado, admin_id_guardado = repo.guardar_vendedor_con_admin.call_args[0]

    assert isinstance(vendedor_guardado, Usuario)
    assert vendedor_guardado.rol == RolUser(RolUser.VENDEDOR)
    assert vendedor_guardado.rol.es_vendedor is True
    assert admin_id_guardado == admin_id


def test_crear_vendedor_hashea_la_password(
    caso_uso: CrearVendedor,
    hasher: Mock,
    repo: Mock,
    admin_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: no se hashea la contraseña (bug de seguridad).
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = admin_existente

    caso_uso.ejecutar(
        nombre="Vendedor",
        email="v@example.com",
        password_plana="Abc123!x",
        admin_id=admin_id,
    )

    hasher.hashear.assert_called_once_with(Password("Abc123!x"))


def test_crear_vendedor_guarda_el_hash_no_la_password_plana(
    caso_uso: CrearVendedor,
    hasher: Mock,
    repo: Mock,
    admin_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se guarda la contraseña en texto plano (bug de seguridad).
    """
    hasher.hashear.return_value = PasswordHash("$2b$12$hash-unico-vendedor")
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = admin_existente

    caso_uso.ejecutar(
        nombre="Vendedor",
        email="v@example.com",
        password_plana="Abc123!x",
        admin_id=admin_id,
    )

    vendedor_guardado = repo.guardar_vendedor_con_admin.call_args[0][0]
    assert vendedor_guardado.password_hash == PasswordHash("$2b$12$hash-unico-vendedor")


# =========================================================================
# Validación: email duplicado
# =========================================================================

def test_crear_vendedor_falla_si_email_ya_existe(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se permiten dos usuarios con el mismo email.
    """
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )


def test_crear_vendedor_no_consulta_admin_si_email_duplicado(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se valida el admin antes del email.

    Orden importa: si el email ya existe, no vale la pena gastar una
    query buscando al admin.
    """
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    repo.obtener_por_id.assert_not_called()


def test_crear_vendedor_no_guarda_si_email_duplicado(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se guarda el vendedor aunque el email ya exista.
    """
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    repo.guardar_vendedor_con_admin.assert_not_called()


# =========================================================================
# Validación: admin no existe
# =========================================================================

def test_crear_vendedor_falla_si_admin_no_existe(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se crea un vendedor sin admin válido.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = None

    with pytest.raises(AdminNoEncontradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )


def test_crear_vendedor_no_guarda_si_admin_no_existe(
    caso_uso: CrearVendedor,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se guarda el vendedor aunque el admin no exista.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = None

    with pytest.raises(AdminNoEncontradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    repo.guardar_vendedor_con_admin.assert_not_called()


def test_crear_vendedor_no_hashea_si_admin_no_existe(
    caso_uso: CrearVendedor,
    hasher: Mock,
    repo: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se hashea antes de validar que el admin exista.

    Orden importa: el hasheo es caro. No gastamos CPU si vamos a fallar.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = None

    with pytest.raises(AdminNoEncontradoException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    hasher.hashear.assert_not_called()


# =========================================================================
# Validación: el usuario no es administrador
# =========================================================================

def test_crear_vendedor_falla_si_usuario_no_es_admin(
    caso_uso: CrearVendedor,
    repo: Mock,
    vendedor_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se puede crear un vendedor asociado a otro vendedor.

    Bug de negocio: solo un admin puede tener vendedores a su cargo.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = vendedor_existente

    with pytest.raises(UsuarioNoEsAdminException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )


def test_crear_vendedor_no_guarda_si_usuario_no_es_admin(
    caso_uso: CrearVendedor,
    repo: Mock,
    vendedor_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se guarda el vendedor aunque el admin no sea admin.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = vendedor_existente

    with pytest.raises(UsuarioNoEsAdminException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    repo.guardar_vendedor_con_admin.assert_not_called()


def test_crear_vendedor_no_hashea_si_usuario_no_es_admin(
    caso_uso: CrearVendedor,
    repo: Mock,
    hasher: Mock,
    vendedor_existente: Mock,
    admin_id: UsuarioId,
) -> None:
    """
    Si falla: se hashea la password antes de validar el rol del admin.

    Orden importa: todas las validaciones antes del hasheo.
    """
    repo.obtener_por_email.return_value = None
    repo.obtener_por_id.return_value = vendedor_existente

    with pytest.raises(UsuarioNoEsAdminException):
        caso_uso.ejecutar(
            nombre="Vendedor",
            email="v@example.com",
            password_plana="Abc123!x",
            admin_id=admin_id,
        )

    hasher.hashear.assert_not_called()
