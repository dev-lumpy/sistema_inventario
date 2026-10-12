# apps/usuarios/exceptions.py
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.domain.exceptions import DomainException

def custom_exception_handler(exc, context):
    if isinstance(exc, DomainException):
        return Response(exc.to_dict(), status=exc.status_code)
    return exception_handler(exc, context)
