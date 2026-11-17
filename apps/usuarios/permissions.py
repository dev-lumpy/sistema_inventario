from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "rol", None) in self.allowed_roles
        )


class IsAdministrador(HasRole):
    allowed_roles = ("administrador",)


class IsVendedor(HasRole):
    allowed_roles = ("vendedor",)


class IsVendedorOrAdministrador(HasRole):
    allowed_roles = ("vendedor", "administrador")


class IsAdministradorOrReadOnly(HasRole):
    allowed_roles = ("administrador", "vendedor")

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return super().has_permission(request, view)
        return IsAdministrador().has_permission(request, view)
