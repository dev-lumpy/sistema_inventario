from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.domain.shared.errors import (
    AuthenticationFailedError,
    BusinessRuleViolation,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

_STATUS = {
    ValidationError: 400,
    BusinessRuleViolation: 400,
    AuthenticationFailedError: 401,
    PermissionDeniedError: 403,
    NotFoundError: 404,
    ConflictError: 409,
}


def _status_para(exc: DomainError) -> int:
    for tipo, status in _STATUS.items():
        if isinstance(exc, tipo):
            return status
    return 400


def responder_domain_error(exc: DomainError) -> Response:
    return Response(
        {
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
        status=_status_para(exc),
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return responder_domain_error(exc)
    return exception_handler(exc, context)
