# apps/usuarios/views/autenticar_usuario.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from core.domain.usuario.value_objects import Email, Password
from core.domain.usuario.exceptions import CredencialesInvalidasException


class AutenticarUsuario(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        # Valida formato (lanza si email/password son inválidos)
        email    = Email(request.data.get('email')).valor
        password = Password(request.data.get('password')).valor

        user = authenticate(request, email=email, password=password)
        if user is None:
            # No distingues entre email no registrado y password mal
            # (buena práctica de seguridad)
            raise CredencialesInvalidasException()

        refresh = RefreshToken.for_user(user)
        refresh['rol'] = user.rol  # type: ignore[attr-defined]
        refresh['username'] = user.get_username()
        response = Response({'status': 'ok'})
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True, secure=False, samesite='Lax', max_age=60 * 15,
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True, secure=False, samesite='Lax', max_age=60 * 60 * 24 * 7,
        )
        return response
