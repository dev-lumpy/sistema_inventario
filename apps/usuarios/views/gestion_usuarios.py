# apps/usuarios/views.py
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from apps.usuarios.models import VendedorORM, UsuarioORM
from apps.usuarios.serializers import VendedorSerializer, UsuarioSerializer
from apps.usuarios.permissions import IsAdministrador


class VendedoresPorAdminView(generics.ListAPIView):
    serializer_class = VendedorSerializer
    permission_classes = [IsAdministrador]

    def get_queryset(self):
        return VendedorORM.objects.filter(
            admins=self.request.user,
            admins__uuid=self.kwargs.get("admin_id"),
        ).select_related("usuarioorm_ptr")


class VendedorDetalleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VendedorSerializer
    lookup_field = "uuid"
    permission_classes = [IsAdministrador]

    def get_queryset(self):
        return VendedorORM.objects.filter(admins=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UsuarioSerializer
        return VendedorSerializer

