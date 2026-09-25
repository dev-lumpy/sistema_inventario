# core/application/usuario/crear_vendedor.py

from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import (
    EstadoUsuario,
    UsuarioId,
    NombreUsuario,
    Email,
    PasswordHash,
    Password,
    RolUser,
)
from core.domain.usuario.exceptions import (
    EmailYaRegistradoException,
    AdminNoEncontradoException,
    UsuarioNoEsAdminException
)
from core.application.ports.password_hasher import PasswordHasher


class CrearVendedor:
    """Caso de uso: crear un usuario con rol vendedor, asociado a un admin."""

    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        password_hasher: PasswordHasher,
    ):
        self.usuario_repo = usuario_repo
        self.password_hasher = password_hasher

    def ejecutar(
        self,
        nombre: str,
        email: str,
        password_plana: str,
        admin_id: UsuarioId,
    ) -> UsuarioId:
        # 1. Validar email único
        email_vo = Email(email)
        existente = self.usuario_repo.obtener_por_email(email_vo)
        if existente is not None:
            raise EmailYaRegistradoException(email)

        # 2. Validar que el admin exista
        admin = self.usuario_repo.obtener_por_id(admin_id)
        if admin is None:
            raise AdminNoEncontradoException(str(admin_id.valor))

        # 3. Validar que el usuario sea administrador
        if not admin.es_administrador():
            raise UsuarioNoEsAdminException(str(admin_id.valor))

        # 4. Hashear contraseña
        hash_ = self.password_hasher.hashear(Password(password_plana))

        # 5. Construir el usuario
        vendedor = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario(nombre),
            email=email_vo,
            activo=EstadoUsuario.activo(),
            password_hash=PasswordHash(hash_.valor),
            rol=RolUser(RolUser.VENDEDOR),
        )

        # 6. Persistir CON admin
        self.usuario_repo.guardar_vendedor_con_admin(vendedor, admin_id)

        return vendedor.id
