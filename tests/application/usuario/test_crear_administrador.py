 # tests/application/usuario/test_crear_administrador.py
"""
Tests del caso de uso CrearAdministrador.

Este test NO toca base de datos ni bcrypt. Mockeamos las dos dependencias
(UsuarioRepository y PasswordHasher) porque el objetivo es testear la
LÓGICA de orquestación del caso de uso, no la infraestructura.
"""

from unittest.mock import Mock

import pytest

from core.application.ports.password_hasher import PasswordHasher
from core.application.usuario.crear_administrador import CrearAdministrador
from core.domain.usuario.exceptions import EmailYaRegistradoException
from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import (
    Email,
    Password,
    PasswordHash,
    RolUser,
    UsuarioId,
)


# =========================================================================
# Fixtures: construyen los mocks y el caso de uso
# =========================================================================

@pytest.fixture
def repo() -> Mock:
    """
    Mock del UsuarioRepository.

    Es un objeto de mentira que se hace pasar por el repo real. No toca
    PostgreSQL. Solo anota las llamadas y devuelve lo que le programemos.
    """
    return Mock(spec=UsuarioRepository)


@pytest.fixture
def hasher() -> Mock:
    """
    Mock del PasswordHasher.

    No hashea de verdad con bcrypt. Por defecto devuelve un hash ficticio
    determinista para poder verificar con qué se guardó.
    """
    mock = Mock(spec=PasswordHasher)
    mock.hashear.return_value = "$2b$12$fakehash"
    return mock


@pytest.fixture
def caso_uso(repo: Mock, hasher: Mock) -> CrearAdministrador:
    """Instancia real del caso de uso, con colaboradores mockeados."""
    return CrearAdministrador(usuario_repo=repo, password_hasher=hasher)


# =========================================================================
# Caso feliz
# =========================================================================

def test_crear_administrador_devuelve_usuario_id(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: el caso de uso no devuelve un UsuarioId.

    Configuramos el repo para que devuelva None (email libre). El caso
    de uso debe completar el flujo y devolver el ID del usuario creado.
    """
    # ¿Qué debe devolver el repo cuando le pidan "obtener_por_email"?
    # → None, que significa "no existe ningún usuario con ese email".
    repo.obtener_por_email.return_value = None

    resultado = caso_uso.ejecutar(
        nombre="Admin Principal",
        email="admin@example.com",
        password_plana="Abc123!x",
    )

    assert isinstance(resultado, UsuarioId)


def test_crear_administrador_consulta_email_antes_de_guardar(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: el caso de uso no verifica que el email sea único.

    Verificamos que el repo recibió una llamada a obtener_por_email con
    un Email VO (normalizado), antes de intentar guardar.
    """
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        nombre="Admin",
        email="admin@example.com",
        password_plana="Abc123!x",
    )

    repo.obtener_por_email.assert_called_once()
    arg = repo.obtener_por_email.call_args[0][0]
    assert isinstance(arg, Email)
    assert arg.valor == "admin@example.com"


def test_crear_administrador_hashea_la_password_plana(
    caso_uso: CrearAdministrador, hasher: Mock, repo: Mock
) -> None:
    """
    Si falla: el caso de uso no hashea la contraseña antes de guardarla.

    Bug de seguridad: se guardaría la contraseña en texto plano.
    """
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        nombre="Admin",
        email="admin@example.com",
        password_plana="Abc123!x",
    )

    hasher.hashear.assert_called_once_with(Password("Abc123!x"))
    print()


def test_crear_administrador_guarda_usuario_con_rol_administrador(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: se crea un usuario como vendedor en vez de administrador.

    Bug clásico: copiar/pegar CrearVendedor y olvidar cambiar el rol.
    """
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        nombre="Admin",
        email="admin@example.com",
        password_plana="Abc123!x",
    )

    repo.guardar_administrador.assert_called_once()
    usuario_guardado = repo.guardar_administrador.call_args[0][0]

    assert isinstance(usuario_guardado, Usuario)
    assert usuario_guardado.rol == RolUser(RolUser.ADMINISTRADOR)
    assert usuario_guardado.rol.es_administrador is True


def test_crear_administrador_guarda_el_hash_no_la_password_plana(
    caso_uso: CrearAdministrador, hasher: Mock, repo: Mock
) -> None:
    """
    Si falla: se guarda la contraseña en texto plano.

    Configuramos el hasher para que devuelva un hash reconocible, y
    verificamos que el usuario guardado tenga ESE hash, no la pass original.
    """
    hasher.hashear.return_value = PasswordHash("$2b$12$hash-unico-123")
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        nombre="Admin",
        email="admin@example.com",
        password_plana="Abc123!x",
    )

    usuario_guardado = repo.guardar_administrador.call_args[0][0]

    assert usuario_guardado.password_hash == PasswordHash("$2b$12$hash-unico-123")
    assert usuario_guardado.password_hash.valor != "Abc123!x"


def test_crear_administrador_normaliza_el_email(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: el email se guarda con espacios o mayúsculas.

    Email normaliza a lower + strip. El usuario guardado debe tener el
    email normalizado, no el input crudo.
    """
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        nombre="Admin",
        email="  ADMIN@Example.COM  ",
        password_plana="Abc123!x",
    )

    usuario_guardado = repo.guardar_administrador.call_args[0][0]
    assert usuario_guardado.email.valor == "admin@example.com"


# =========================================================================
# Email duplicado
# =========================================================================

def test_crear_administrador_falla_si_email_ya_existe(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: se permiten dos administradores con el mismo email.

    Configuramos el repo para que devuelva un Usuario (algo distinto de
    None), simulando que el email ya está registrado.
    """
    # ¿Qué debe devolver el repo cuando le pidan "obtener_por_email"?
    # → un Usuario (mock), que significa "sí existe alguien con ese email".
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Admin",
            email="admin@example.com",
            password_plana="Abc123!x",
        )


def test_crear_administrador_no_guarda_si_email_esta_duplicado(
    caso_uso: CrearAdministrador, repo: Mock
) -> None:
    """
    Si falla: se guarda el usuario aunque el email esté duplicado.

    Bug real: la validación existe pero no corta el flujo. Verificamos
    que guardar_administrador NO se llamó.
    """
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Admin",
            email="admin@example.com",
            password_plana="Abc123!x",
        )

    repo.guardar_administrador.assert_not_called()


def test_crear_administrador_no_hashea_si_email_esta_duplicado(
    caso_uso: CrearAdministrador, repo: Mock, hasher: Mock
) -> None:
    """
    Si falla: se hashea la contraseña aunque el email esté duplicado.

    Eficiencia + orden: validar primero, hashear después. El hasheo
    es caro (bcrypt tarda ~100ms). No gastamos CPU si vamos a fallar.
    """
    repo.obtener_por_email.return_value = Mock(spec=Usuario)

    with pytest.raises(EmailYaRegistradoException):
        caso_uso.ejecutar(
            nombre="Admin",
            email="admin@example.com",
            password_plana="Abc123!x",
        )

    hasher.hashear.assert_not_called()
