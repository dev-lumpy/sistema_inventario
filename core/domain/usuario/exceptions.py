# core/domain/usuario/exceptions.py
"""Excepciones del dominio Usuario"""

from core.domain.shared.exceptions import DomainException



class CredencialesInvalidasException(DomainException):
    """
    Se lanza cuando el email no existe o la contraseña es incorrecta.
    No distingue entre ambos casos por seguridad (evita enumeración de usuarios).
    """
    def __init__(self):
        super().__init__(
            code="CREDENCIALES_INVALIDAS",
            message="Invalid credentials",
            message_key="auth.INVALID_CREDENTIALS",
            status_code=401,
        )


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


class EmailNoRegistradoException(DomainException):
    """El email es válido pero no existe en el sistema."""
    def __init__(self, email: str):
        super().__init__(
            code="EMAIL_NO_REGISTRADO",
            message="Email not registered",
            message_key="email.NOT_REGISTERED",
            status_code=404,
            field="email",
            email=email,
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


class EstadoUsuarioInvalidoException(DomainException):
    """
    Se lanza cuando se intenta construir un Value Object de estado
    de usuario con un valor que no está dentro de los valores válidos.
    """

    def __init__(self, valor: str):
        super().__init__(
            code="ESTADO_USUARIO_INVALIDO",
            message="Invalid user status",
            message_key="user.ESTADO_INVALIDO",
            status_code=422,          # 422 Unprocessable Entity (error de validación de dominio)
            field="estado",
            valor=valor,              # se interpola en {valor} del mensaje i18n
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
