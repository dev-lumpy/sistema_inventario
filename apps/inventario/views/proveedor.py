from rest_framework.generics import UpdateAPIView, CreateAPIView, ListAPIView
from rest_framework.views import APIView, Response
from rest_framework import serializers
 
from apps.inventario.models import Proveedor
from apps.inventario.services.movimiento_service import registrar_entrada_stock
from apps.inventario.serializers import (
    ProveedorSelectSerializer,
    EntradaStockSerializer
)

class ProveedorSelectAPIView(ListAPIView):
    queryset = Proveedor.objects.filter(activo=True).order_by('nombre')
    serializer_class = ProveedorSelectSerializer
    pagination_class = None


class RegistrarEntradaStockAPIView(APIView):
    def post(self, request):
        serializer = EntradaStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mov = registrar_entrada_stock(
            producto=serializer.validated_data['producto'],
            cantidad=serializer.validated_data['cantidad'],
            proveedor=serializer.validated_data['proveedor'],
        )

        producto = mov.producto
        return Response(
            {
                'mensaje': 'Entrada registrada correctamente.',
                'movimiento_id': mov.id,
                'producto_id': producto.id,
                'producto': producto.nombre,
                'cantidad': mov.cantidad,
                'proveedor': mov.proveedor.nombre,
                'nuevo_stock': producto.stock_actual,
            },
            status=status.HTTP_201_CREATED,
        )
