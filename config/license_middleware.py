from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from config.license import verify_license


class LicenseMiddleware(MiddlewareMixin):
    """Verifica la licencia en cada request. Si no es válida, bloquea el acceso."""

    def process_request(self, request):
        # No bloquear rutas de administración del sistema
        if request.path.startswith("/license/"):
            return None

        license_data = verify_license()
        if license_data is None:
            return HttpResponse(
                "<h1>Licencia inválida o expirada</h1>"
                "<p>Contacta al desarrollador para obtener una licencia válida.</p>",
                status=403,
            )
        return None