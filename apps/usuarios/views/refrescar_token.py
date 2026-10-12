# apps/usuarios/views/refrescar_token.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response

class RefrescarToken(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        raw_refresh = request.COOKIES.get('refresh_token')
        if not raw_refresh:
            return Response({'error': 'No hay refresh token'}, status=401)

        try:
            refresh = RefreshToken(raw_refresh)
        except TokenError:
            return Response({'error': 'Refresh token inválido o expirado'}, status=401)

        response = Response({'status': 'ok'})
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=60 * 15,
        )
        # Opcional: rotar el refresh token también
        # refresh.set_jti()
        # refresh.set_exp()
        # response.set_cookie('refresh_token', str(refresh), ...)

        return response
