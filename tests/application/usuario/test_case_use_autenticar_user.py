# tests/application/usuario/test_autenticar_usuario.py
"""
Tests del caso de uso AutenticarUsuario.

AutenticarUsuario NO distingue roles: solo valida email + activo + password.
El rol se refleja en el output, pero no condiciona el flujo.

Por eso parametrizamos los tests por rol: verificamos que la lógica es
la misma sin importar si el usuario es vendedor o administrador.
"""

from unittest.mock import Mock

import pytest

from core.application.ports.password_hasher import PasswordHasher
from core.application.usuario.autenticar_usuario import (
    AutenticarUsuario,
    AutenticarUsuarioInput,
)
from core.domain.usuario.exceptions import UsuarioInactivoException
from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.usuario import EstadoUsuario, Usuario
from core.domain.usuario.value_objects import (
    Email,
    NombreUsuario,
    PasswordHash,
    RolUser,
    UsuarioId,
    EstadoUsuario
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
    return Mock(spec=PasswordHasher)


@pytest.fixture
def caso_uso(repo: Mock, hasher: Mock) -> AutenticarUsuario:
    return AutenticarUsuario(usuario_repo=repo, password_hasher=hasher)


def _crear_usuario(rol: RolUser, activo: EstadoUsuario = EstadoUsuario.activo()) -> Usuario:
    """
    Helper para construir un Usuario real. Evitamos duplicar el constructor
    en cada test.
    """
    return Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Juan"),
        email=Email("juan@test.com"),
        password_hash=PasswordHash("$2b$12$hash"),
        rol=rol,
        activo=activo,
    )


@pytest.fixture
def usuario_activo() -> Usuario:
    """Usuario vendedor, activo. Fixture por defecto."""
    return _crear_usuario(RolUser(RolUser.VENDEDOR), activo=EstadoUsuario.activo())


@pytest.fixture
def usuario_inactivo() -> Usuario:
    """Usuario vendedor, inactivo."""
    return _crear_usuario(RolUser(RolUser.VENDEDOR), activo=EstadoUsuario.inactivo())


# =========================================================================
# Roles soportados (para parametrizar)
# =========================================================================

ROLES_VALIDOS = [
    pytest.param(RolUser(RolUser.VENDEDOR), id="vendedor"),
    pytest.param(RolUser(RolUser.ADMINISTRADOR), id="administrador"),
]


# =========================================================================
# Caso feliz: parametrizado por rol
# =========================================================================

@pytest.mark.parametrize("rol", ROLES_VALIDOS)
def test_autenticar_devuelve_datos_para_cualquier_rol(
    caso_uso, repo, hasher, rol
):
    """
    Si falla: AutenticarUsuario no funciona con alguno de los roles.

    No importa si es vendedor o administrador: la lógica es la misma.
    El test parametrizado verifica que ambos caminos funcionan.
    """
    usuario = _crear_usuario(rol, activo=EstadoUsuario.activo())

    repo.obtener_por_email.return_value = usuario
    hasher.verificar.return_value = True

    resultado = caso_uso.ejecutar(
        AutenticarUsuarioInput(
            email=usuario.email.valor,
            password="Abc123!x",
        )
    )

    assert resultado is not None
    # Comparamos contra el usuario real, no contra literales hardcodeados.
    assert resultado.usuario_id == str(usuario.id)
    assert resultado.nombre == usuario.nombre.valor
    assert resultado.email == usuario.email.valor
    assert resultado.rol == usuario.rol.valor


@pytest.mark.parametrize("rol", ROLES_VALIDOS)
def test_autenticar_verifica_la_password_con_el_hash_guardado(
    caso_uso, repo, hasher, rol
):
    """
    Si falla: no se usa el hash almacenado para verificar.

    Debe usar `usuario.password_hash.valor`, no otra cosa.
    """
    usuario = _crear_usuario(rol, activo=EstadoUsuario.activo())

    repo.obtener_por_email.return_value = usuario
    hasher.verificar.return_value = True

    caso_uso.ejecutar(
        AutenticarUsuarioInput(
            email=usuario.email.valor,
            password="Abc123!x",
        )
    )

    hasher.verificar.assert_called_once_with(
        "Abc123!x", usuario.password_hash.valor
    )


# =========================================================================
# Email no registrado
# =========================================================================

def test_autenticar_devuelve_none_si_usuario_no_existe(caso_uso, repo):
    """
    Si falla: se autentica un usuario inexistente.
    """
    repo.obtener_por_email.return_value = None

    resultado = caso_uso.ejecutar(
        AutenticarUsuarioInput(email="nadie@test.com", password="Abc123!x")
    )

    assert resultado is None


def test_autenticar_no_verifica_password_si_usuario_no_existe(
    caso_uso, repo, hasher
):
    """
    Si falla: se llama al hasher aunque no haya usuario.

    Eficiencia + seguridad: no gastar CPU hasheando sin motivo.
    """
    repo.obtener_por_email.return_value = None

    caso_uso.ejecutar(
        AutenticarUsuarioInput(email="nadie@test.com", password="Abc123!x")
    )

    hasher.verificar.assert_not_called()


# =========================================================================
# Password incorrecta
# =========================================================================

@pytest.mark.parametrize("rol", ROLES_VALIDOS)
def test_autenticar_devuelve_none_si_password_no_coincide(
    caso_uso, repo, hasher, rol
):
    """
    Si falla: se autentica con contraseña incorrecta (bug de seguridad).

    Parametrizado por rol para confirmar que la verificación de password
    no depende del rol.
    """
    usuario = _crear_usuario(rol, activo=EstadoUsuario.activo())

    repo.obtener_por_email.return_value = usuario
    hasher.verificar.return_value = False   # ← pass incorrecta

    resultado = caso_uso.ejecutar(
        AutenticarUsuarioInput(
            email=usuario.email.valor,
            password="mala",
        )
    )

    assert resultado is None


# =========================================================================
# Usuario inactivo
# =========================================================================

def test_autenticar_falla_si_usuario_inactivo(
    caso_uso, repo, usuario_inactivo
):
    """
    Si falla: se permite login a un usuario desactivado.

    `verificar_activo()` del Usuario lanza UsuarioInactivoException.
    """
    repo.obtener_por_email.return_value = usuario_inactivo

    with pytest.raises(UsuarioInactivoException):
        caso_uso.ejecutar(
            AutenticarUsuarioInput(
                email=usuario_inactivo.email.valor,
                password="Abc123!x",
            )
        )


def test_autenticar_no_verifica_password_si_usuario_inactivo(
    caso_uso, repo, hasher, usuario_inactivo
):
    """
    Si falla: se verifica la contraseña de un usuario inactivo.

    Orden importa: verificar_activo va antes de hashear/verificar.
    """
    repo.obtener_por_email.return_value = usuario_inactivo

    with pytest.raises(UsuarioInactivoException):
        caso_uso.ejecutar(
            AutenticarUsuarioInput(
                email=usuario_inactivo.email.valor,
                password="Abc123!x",
            )
        )

    hasher.verificar.assert_not_called()
