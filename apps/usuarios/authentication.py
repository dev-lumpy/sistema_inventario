# apps/usuarios/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = None

        # 1. Header (móvil, Postman)
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)

        # 2. Fallback a cookie si no hay header
        if raw_token is None:
            raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError):
            # Si el token del header falla, intenta la cookie
            cookie_token = request.COOKIES.get('access_token')
            if cookie_token and cookie_token != raw_token:
                try:
                    validated_token = self.get_validated_token(cookie_token)
                except (InvalidToken, TokenError):
                    return None
            else:
                return None

        return self.get_user(validated_token), validated_token
