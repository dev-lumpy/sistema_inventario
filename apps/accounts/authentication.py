from __future__ import annotations

from rest_framework.authentication import BaseAuthentication

from apps.accounts.models import Usuario as UsuarioORM


class UsuarioSesion:
    def __init__(self, orm: UsuarioORM, rol: str) -> None:
        self._orm = orm
        self.rol = rol

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return self._orm.activo

    @property
    def pk(self) -> int:
        return self._orm.pk

    @property
    def id(self) -> int:
        return self._orm.pk

    @property
    def username(self) -> str:
        return self._orm.user_name

    @property
    def email(self) -> str:
        return self._orm.correo

    @property
    def nombre(self) -> str:
        return self._orm.nombre

    def get_username(self) -> str:
        return self.username

    def __str__(self) -> str:
        return self.username


class SessionUsuarioAuthentication(BaseAuthentication):
    def authenticate(self, request):
        usuario_id = request.session.get("usuario_id")
        rol = request.session.get("rol")
        if not usuario_id or not rol:
            return None

        orm = UsuarioORM.objects.filter(pk=usuario_id, activo=True).first()
        if orm is None:
            return None
        return (UsuarioSesion(orm, rol), None)

    def authenticate_header(self, request) -> str:
        return "Session"
