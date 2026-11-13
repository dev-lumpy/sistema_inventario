# apps/usuarios/views.py
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from apps.usuarios.models import VendedorORM, UsuarioORM
from apps.usuarios.serializers import VendedorSerializer, UsuarioSerializer


class VendedoresPorAdminView(generics.ListAPIView):
    serializer_class = VendedorSerializer

    def get_queryset(self):
        admin_id = self.kwargs.get("admin_id")
        # Opcional: validar UUID
        return VendedorORM.objects.filter(admins__uuid=admin_id).select_related("usuarioorm_ptr")


class VendedorDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VendedorORM.objects.all()
    serializer_class = VendedorSerializer
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UsuarioSerializer
        return VendedorSerializer

