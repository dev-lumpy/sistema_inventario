from __future__ import annotations

from typing import Any


class DomainError(Exception):
    code = "DOMAIN_ERROR"

    def __init__(self, message: str, **context: Any) -> None:
        self.message = message
        self.context = context
        super().__init__(message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"


class BusinessRuleViolation(DomainError):
    code = "BUSINESS_RULE_VIOLATION"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    code = "CONFLICT"


class PermissionDeniedError(DomainError):
    code = "PERMISSION_DENIED"


class AuthenticationFailedError(DomainError):
    code = "AUTHENTICATION_FAILED"
