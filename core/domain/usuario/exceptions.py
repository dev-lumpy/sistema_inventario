# core/domain/usuario/exceptions.py
"""Excepciones del dominio Usuario"""

from core.domain.shared.exceptions import DomainException


class UsuarioIdInvalidoException(DomainException):
    """
    Excepción única para cualquier fallo al construir un UsuarioId.
    El detalle (motivo) va en `code` y `message_key`.
    """

    def __init__(
        self,
        usuario_id: str,
        code: str = "USUARIO_ID_INVALIDO",
        message_key: str = "user.ID_INVALID",
        message: str = "Invalid user ID",
        **ctx,
    ):
        super().__init__(
            code=code,
            message=message,
            message_key=message_key,
            status_code=400,
            field="usuario_id",
            usuario_id=str(usuario_id),
            **ctx,
        )


class EmailInvalidoException(DomainException):
    """
    Excepción única para todas las violaciones del VO Email.
    El motivo se expresa como key del catálogo ('email.EMPTY', etc.).
    """
    def __init__(self, motivo_key: str, **params):
        super().__init__(
            code="EMAIL_INVALIDO",
            message="Invalid email",
            message_key=f"email.{motivo_key}",
            status_code=400,
            field="email",
            **params,
        )


class UsuarioNoEncontradoException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="USUARIO_NO_ENCONTRADO",
            message="User not found",
            message_key="user.NOT_FOUND",
            status_code=404,
            field="usuario_id",
            usuario_id=usuario_id,
        )


class UsuarioInactivoException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="USUARIO_INACTIVO",
            message="User inactive",
            message_key="user.INACTIVE",
            status_code=403,
            field="usuario_id",
            usuario_id=usuario_id,
        )


class PermisoDenegadoException(DomainException):
    def __init__(self, accion: str = ""):
        super().__init__(
            code="PERMISO_DENEGADO",
            message="Permission denied",
            message_key="core.PERMISSION_DENIED",
            status_code=403,
            field="accion",
            accion=accion,
        )

class NombreUsuarioInvalidoException(DomainException):
    """
    Excepción única para todas las violaciones de reglas del VO NombreUsuario.
    El motivo se expresa como key del catálogo ('name.TOO_SHORT', etc.).
    """
    def __init__(self, motivo_key: str, **params):
        super().__init__(
            code="NOMBRE_USUARIO_INVALIDO",
            message="Invalid username",
            message_key=f"name.{motivo_key}",
            status_code=400,
            field="nombre",
            **params,
        )

class PasswordHashInvalidoException(DomainException):
    """Errores del VO PasswordHash."""
    def __init__(self, motivo_key: str, **params):
        super().__init__(
            code="PASSWORD_HASH_INVALIDO",
            message="Invalid password hash",
            message_key=f"password.{motivo_key}",
            status_code=400,
            field="password_hash",
            **params,
        )


class PasswordInvalidaException(DomainException):
    """Errores del VO Password."""
    def __init__(self, motivo_key: str, **params):
        super().__init__(
            code="PASSWORD_INVALIDA",
            message="Invalid password",
            message_key=f"password.{motivo_key}",
            status_code=400,
            field="password",
            **params,
        )


class RolInvalidoException(DomainException):
    """
    Excepción única para todas las violaciones de reglas del VO RolUser.
    El motivo se expresa como key del catálogo ('role.INVALID', etc.).
    """
    def __init__(self, motivo_key: str, **params):
        super().__init__(
            code="ROL_INVALIDO",
            message="Invalid role",
            message_key=f"role.{motivo_key}",
            status_code=400,
            field="rol",
            **params,
        )


# core/domain/usuario/exceptions.py   (o donde tengas las excepciones de usuario)

class EmailYaRegistradoException(DomainException):
    def __init__(self, email: str):
        super().__init__(
            code="EMAIL_YA_REGISTRADO",
            message="Email already registered",
            message_key="email.ALREADY_EXISTS",
            status_code=409,
            field="email",
            email=email,
        )



class AdminNoEncontradoException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="ADMIN_NO_ENCONTRADO",
            message="Administrator not found",
            message_key="admin.NOT_FOUND",
            status_code=404,
            field="usuario_id",
            usuario_id=usuario_id,
        )


class UsuarioNoEsAdminException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="USUARIO_NO_ES_ADMIN",
            message="User is not an administrator",
            message_key="admin.NOT_ADMIN",
            status_code=403,
            field="usuario_id",
            usuario_id=usuario_id,
        )
