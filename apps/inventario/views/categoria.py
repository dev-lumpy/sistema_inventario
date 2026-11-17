# apps/inventario/views.py
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.views import APIView
from apps.inventario.models import Categoria
from apps.inventario.serializers import (
    CategoriaSelectSerializer,
    CategoriaSerializer,
)
from apps.usuarios.permissions import IsAdministrador, IsAdministradorOrReadOnly

class CategoriaSelectAPIView(ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSelectSerializer
    pagination_class = None    # sin paginación, son pocas
    permission_classes = [IsAdministradorOrReadOnly]


class AddCategoriaAPIView(CreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdministrador]


class CategoriaDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'pk'
    permission_classes = [IsAdministradorOrReadOnly]
