# core/application/usuario/crear_administrador.py

from core.domain.usuario.repository import UsuarioRepository
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import (
    EstadoUsuario,
    Password,
    UsuarioId,
    NombreUsuario,
    Email,
    PasswordHash,
    RolUser,
)
from core.domain.usuario.exceptions import EmailYaRegistradoException
from core.application.ports.password_hasher import PasswordHasher


class CrearAdministrador:
    """Caso de uso: crear un usuario con rol administrador."""

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
    ) -> UsuarioId:
        # 1. Validar email único
        email_vo = Email(email)
        existente = self.usuario_repo.obtener_por_email(email_vo)
        if existente is not None:
            raise EmailYaRegistradoException(email)

        # 2. Hashear contraseña
        hash_ = self.password_hasher.hashear(Password(password_plana))

        # 3. Construir el usuario
        admin = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario(nombre),
            email=email_vo,
            activo=EstadoUsuario.activo(),
            password_hash=hash_,
            rol=RolUser(RolUser.ADMINISTRADOR)
        )

        # 4. Persistir
        self.usuario_repo.guardar_administrador(admin)

        return admin.id
