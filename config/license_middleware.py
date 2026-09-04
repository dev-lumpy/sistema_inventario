from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from config.license import get_machine_id, verify_license


class LicenseMiddleware(MiddlewareMixin):
    """Verifica la licencia en cada request. Si no es válida, bloquea el acceso."""

    def process_request(self, request):
        # No bloquear rutas de administración del sistema
        if request.path.startswith("/license/"):
            return None

        license_data = verify_license()
        if license_data is None:
            return render(
                request,
                "license_invalid.html",
                {"machine_id": get_machine_id()},
                status=403,
            )
        return None