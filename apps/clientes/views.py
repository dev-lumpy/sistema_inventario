from django.shortcuts import render
from django.http import JsonResponse

from config.license import get_machine_id, verify_license


# Create your views here.
def dashboard(request):
    return render(request, 'index.html')

def error_500(request):
    return render(request, 'error-500.html')

def license_info(request):
    lic = verify_license()
    return JsonResponse({
        "machine_id": get_machine_id(),
        "license_valid": lic is not None,
        "license_data": lic,
    })
