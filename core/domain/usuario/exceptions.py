# core/domain/usuario/exceptions.py
"""Excepciones del dominio Usuario"""

from core.domain.shared.exceptions import DomainException


class UsuarioIdInvalidoException(DomainException):
    def __init__(self, id: str):
        super().__init__(
            code="USUARIO_ID_INVALIDO",
            message=f"ID de usuario inválido: {id}",
            status_code=400,
            field="ID de usuario",
            id=id,
        )


class EmailInvalidoException(DomainException):
    def __init__(self, email: str):
        super().__init__(
            code="EMAIL_INVALIDO",
            message=f"Email inválido: {email}",
            status_code=400,
            email=email,
        )


class UsuarioNoEncontradoException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="USUARIO_NO_ENCONTRADO",
            message=f"Usuario no encontrado: {usuario_id}",
            status_code=404,
            usuario_id=usuario_id,
        )


class UsuarioInactivoException(DomainException):
    def __init__(self, usuario_id: str):
        super().__init__(
            code="USUARIO_INACTIVO",
            message=f"Usuario inactivo: {usuario_id}",
            status_code=403,
            usuario_id=usuario_id,
        )


class PermisoDenegadoException(DomainException):
    def __init__(self, accion: str = ""):
        super().__init__(
            code="PERMISO_DENEGADO",
            message=f"Permiso denegado: {accion}",
            status_code=403,
            accion=accion,
        )