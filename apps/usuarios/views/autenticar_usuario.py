# apps/usuarios/views/autenticar_usuario.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from core.domain.usuario.value_objects import Email, Password
from core.domain.usuario.exceptions import CredencialesInvalidasException
from apps.usuarios.serializers import LoginSerializer


class AutenticarUsuario(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        refresh['rol'] = user.rol
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
