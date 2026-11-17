from __future__ import annotations

from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "administrador"
        )


class EsVendedor(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "vendedor"
        )


class EsAdministradorOVendedor(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) in ("administrador", "vendedor")
        )
