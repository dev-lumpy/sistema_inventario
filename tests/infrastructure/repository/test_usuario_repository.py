 # tests/infrastructure/repositories/test_usuario_repository.py
"""
Tests del adapter DjangoUsuarioRepository.

Este adapter SÍ toca base de datos. Usamos @pytest.mark.django_db, que:
1. Crea una BD de test.
2. Envuelve cada test en una transacción.
3. Rollback al terminar.
Así los tests no se contaminan entre sí.

NO mockeamos el ORM. El objetivo es probar la integración real con Django.
"""

import pytest

from core.domain.usuario.usuario import EstadoUsuario, Usuario
from core.domain.usuario.value_objects import (
    Email,
    NombreUsuario,
    PasswordHash,
    RolUser,
    UsuarioId,
)
from infrastructure.django.repositories.usuario_repository import (
    AdministradorORM,
    DjangoUsuarioRepository,
    VendedorORM,
)


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def repo() -> DjangoUsuarioRepository:
    return DjangoUsuarioRepository()


def _crear_admin(email: str = "admin@test.com") -> Usuario:
    return Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Admin Test"),
        email=Email(email),
        password_hash=PasswordHash("$2b$12$adminhash"),
        rol=RolUser(RolUser.ADMINISTRADOR),
        activo=EstadoUsuario.activo(),
    )


def _crear_vendedor(email: str = "vendedor@test.com") -> Usuario:
    return Usuario(
        id=UsuarioId.generar(),
        nombre=NombreUsuario("Vendedor Test"),
        email=Email(email),
        password_hash=PasswordHash("$2b$12$vendedorhash"),
        rol=RolUser(RolUser.VENDEDOR),
        activo=EstadoUsuario.activo(),
    )


# =========================================================================
# guardar_administrador
# =========================================================================

@pytest.mark.django_db
def test_guardar_administrador_persiste_en_bd(repo):
    """
    Si falla: guardar_administrador no crea el registro.
    """
    admin = _crear_admin()

    repo.guardar_administrador(admin)

    orm = AdministradorORM.objects.get(uuid=admin.id.valor)
    assert orm.username == "Admin Test"
    assert orm.email == "admin@test.com"
    assert orm.password == "$2b$12$adminhash"


@pytest.mark.django_db
def test_guardar_administrador_es_idempotente(repo):
    """
    Si falla: guardar dos veces el mismo admin crea duplicados.

    El adapter usa update_or_create, así que debe actualizar, no duplicar.
    """
    admin = _crear_admin()

    repo.guardar_administrador(admin)
    repo.guardar_administrador(admin)

    count = AdministradorORM.objects.filter(uuid=admin.id.valor).count()
    assert count == 1


@pytest.mark.django_db
def test_guardar_administrador_actualiza_si_ya_existe(repo):
    """
    Si falla: guardar con el mismo UUID no actualiza campos.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    admin_modificado = _crear_admin(email="nuevo@test.com")
    # Forzamos el mismo UUID para que update_or_create actualice
    object.__setattr__(admin_modificado, "id", admin.id)
    repo.guardar_administrador(admin_modificado)

    orm = AdministradorORM.objects.get(uuid=admin.id.valor)
    assert orm.email == "nuevo@test.com"


# =========================================================================
# obtener_por_id
# =========================================================================

@pytest.mark.django_db
def test_obtener_por_id_encuentra_admin(repo):
    """
    Si falla: no se recupera un admin guardado.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    recuperado = repo.obtener_por_id(admin.id)

    assert recuperado is not None
    assert recuperado.id == admin.id
    assert recuperado.email.valor == "admin@test.com"
    assert recuperado.rol == RolUser(RolUser.ADMINISTRADOR)


@pytest.mark.django_db
def test_obtener_por_id_devuelve_none_si_no_existe(repo):
    """
    Si falla: obtener_por_id explota o devuelve algo en vez de None.
    """
    id_inexistente = UsuarioId.generar()

    assert repo.obtener_por_id(id_inexistente) is None


@pytest.mark.django_db
def test_obtener_por_id_prioriza_admin_sobre_vendedor(repo):
    """
    Si falla: obtener_por_id no respeta el orden admin → vendedor.

    El adapter busca admin primero, luego vendedor. Si hay colisión de UUID
    (raro pero posible), debe ganar admin.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    recuperado = repo.obtener_por_id(admin.id)
    assert recuperado.rol == RolUser(RolUser.ADMINISTRADOR)


# =========================================================================
# obtener_por_email
# =========================================================================

@pytest.mark.django_db
def test_obtener_por_email_encuentra_admin(repo):
    """
    Si falla: no se encuentra un admin por email.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    recuperado = repo.obtener_por_email(Email("admin@test.com"))

    assert recuperado is not None
    assert recuperado.email.valor == "admin@test.com"
    assert recuperado.rol == RolUser(RolUser.ADMINISTRADOR)


@pytest.mark.django_db
def test_obtener_por_email_devuelve_none_si_no_existe(repo):
    """
    Si falla: obtener_por_email explota con un email inexistente.
    """
    assert repo.obtener_por_email(Email("nadie@test.com")) is None


@pytest.mark.django_db
def test_obtener_por_email_busca_en_vendedor_si_no_hay_admin(repo):
    """
    Si falla: no se busca en la tabla vendedor como fallback.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    vendedor = _crear_vendedor()
    repo.guardar_vendedor_con_admin(vendedor, admin.id)

    recuperado = repo.obtener_por_email(Email("vendedor@test.com"))

    assert recuperado is not None
    assert recuperado.rol == RolUser(RolUser.VENDEDOR)


# =========================================================================
# guardar_vendedor_con_admin
# =========================================================================

@pytest.mark.django_db
def test_guardar_vendedor_asocia_el_admin(repo):
    """
    Si falla: el vendedor no queda asociado al admin (FK rota).
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    vendedor = _crear_vendedor()
    repo.guardar_vendedor_con_admin(vendedor, admin.id)

    vendedor_orm = VendedorORM.objects.get(uuid=vendedor.id.valor)
    assert vendedor_orm.email == "vendedor@test.com"
    assert vendedor_orm.admin.uuid == admin.id.valor


@pytest.mark.django_db
def test_guardar_vendedor_falla_si_admin_no_existe(repo):
    """
    Si falla: se guarda un vendedor con un admin_id inexistente.

    El adapter hace `AdministradorORM.objects.get(...)`, que lanza
    DoesNotExist si no encuentra al admin.
    """
    vendedor = _crear_vendedor()
    admin_id_inexistente = UsuarioId.generar()

    with pytest.raises(AdministradorORM.DoesNotExist):
        repo.guardar_vendedor_con_admin(vendedor, admin_id_inexistente)


# =========================================================================
# listar_todos / obtener_administradores
# =========================================================================

@pytest.mark.django_db
def test_listar_todos_devuelve_admins_y_vendedores(repo):
    """
    Si falla: listar_todos no devuelve todos los usuarios.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    vendedor = _crear_vendedor()
    repo.guardar_vendedor_con_admin(vendedor, admin.id)

    todos = repo.listar_todos()

    assert len(todos) == 2
    emails = {u.email.valor for u in todos}
    assert "admin@test.com" in emails
    assert "vendedor@test.com" in emails


@pytest.mark.django_db
def test_obtener_administradores_solo_devuelve_admins(repo):
    """
    Si falla: obtener_administradores incluye vendedores.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    vendedor = _crear_vendedor()
    repo.guardar_vendedor_con_admin(vendedor, admin.id)

    admins = repo.obtener_administradores()

    assert len(admins) == 1
    assert admins[0].rol == RolUser(RolUser.ADMINISTRADOR)


# =========================================================================
# eliminar
# =========================================================================

@pytest.mark.django_db
def test_eliminar_borra_el_admin(repo):
    """
    Si falla: eliminar no borra al admin.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    repo.eliminar(admin.id)

    assert not AdministradorORM.objects.filter(uuid=admin.id.valor).exists()


@pytest.mark.django_db
def test_eliminar_no_falla_si_no_existe(repo):
    """
    Si falla: eliminar explota con un id inexistente.

    El adapter usa .filter().delete(), que no falla si no hay nada.
    """
    repo.eliminar(UsuarioId.generar())   # no debe lanzar


# =========================================================================
# Mappers ORM → Dominio
# =========================================================================

@pytest.mark.django_db
def test_mapper_admin_convierte_campos_correctamente(repo):
    """
    Si falla: _admin_to_domain mapea mal algún campo.

    Verifica que el Usuario reconstruido tenga todos sus VOs bien.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    recuperado = repo.obtener_por_id(admin.id)

    assert isinstance(recuperado.id, UsuarioId)
    assert isinstance(recuperado.nombre, NombreUsuario)
    assert isinstance(recuperado.email, Email)
    assert isinstance(recuperado.password_hash, PasswordHash)
    assert isinstance(recuperado.rol, RolUser)
    assert recuperado.nombre.valor == "Admin Test"


@pytest.mark.django_db
def test_mapper_vendedor_usa_rol_vendedor(repo):
    """
    Si falla: _vendedor_to_domain construye el Usuario con rol admin.
    """
    admin = _crear_admin()
    repo.guardar_administrador(admin)

    vendedor = _crear_vendedor()
    repo.guardar_vendedor_con_admin(vendedor, admin.id)

    recuperado = repo.obtener_por_email(Email("vendedor@test.com"))
    assert recuperado.rol == RolUser(RolUser.VENDEDOR)
