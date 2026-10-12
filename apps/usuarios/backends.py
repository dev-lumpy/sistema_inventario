# apps/usuarios/backends.py
from typing import Optional, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import check_password

from apps.usuarios.models import UsuarioORM
from core.domain.usuario.exceptions import CredencialesInvalidasException

User = get_user_model()

class UsuarioORMBackend(BaseBackend):
    def authenticate(
        self,
        request,
        email=None,
        password=None,
        **kwargs,
    ) -> Optional[AbstractBaseUser]:
        try:
            user = UsuarioORM.objects.get(email=email)
        except UsuarioORM.DoesNotExist:
            return None

        if not check_password(password, user.password):
            raise CredencialesInvalidasException() 

        return cast(AbstractBaseUser, user)

    def get_user(self, user_id) -> Optional[AbstractBaseUser]:
        try:
            user = UsuarioORM.objects.get(pk=user_id)
        except UsuarioORM.DoesNotExist:
            return None

        return cast(AbstractBaseUser, user)


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username
        if email is None or password is None:
            return None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Ejecuta el hash igual para no filtrar info por timing
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
