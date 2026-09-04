from pathlib import Path

from django.contrib.admin.options import messages
from django.shortcuts import render, get_object_or_404 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from config.license import get_machine_id, verify_license


# Create your views here.
def license_info(request):
    lic = verify_license()
    return JsonResponse({
        "machine_id": get_machine_id(),
        "license_valid": lic is not None,
        "license_data": lic,
    })

@csrf_exempt
@require_http_methods(["POST"])
def activar_licencia(request):
    # Aun no hay logica para esto
    message = ""

    if request.FILES:
        archivo = request.FILES['archivo_licencia']

        with open(Path(settings.BASE_DIR), 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        return JsonResponse({
            'status': 'success',
            'message': f"Su licencia se registro correctamente"
        })

    return JsonResponse({
        'status': 'fail',
        'message': f"No se pudo leer el archivo"
    })


