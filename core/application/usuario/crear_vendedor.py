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
        admin_id: UsuarioId | None = None,
        admin_ids: list[UsuarioId] | None = None,
    ) -> UsuarioId:
        # 1. Validar email único
        email_vo = Email(email)
        existente = self.usuario_repo.obtener_por_email(email_vo)
        if existente is not None:
            raise EmailYaRegistradoException(email)

        # 2. Validar admins (puede no tener ninguno)
        ids_admins = list(admin_ids) if admin_ids else (
            [admin_id] if admin_id is not None else []
        )
        for id_admin in ids_admins:
            admin = self.usuario_repo.obtener_por_id(id_admin)
            if admin is None:
                raise AdminNoEncontradoException(str(id_admin.valor))

            if not admin.es_administrador():
                raise UsuarioNoEsAdminException(str(id_admin.valor))

        # 3. Hashear contraseña
        hash_ = self.password_hasher.hashear(Password(password_plana))

        # 4. Construir el usuario
        vendedor = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario(nombre),
            email=email_vo,
            activo=EstadoUsuario.activo(),
            password_hash=PasswordHash(hash_.valor),
            rol=RolUser(RolUser.VENDEDOR),
        )

        # 5. Persistir con los admins indicados (o sin ninguno)
        self.usuario_repo.guardar_vendedor(vendedor, ids_admins)

        return vendedor.id
