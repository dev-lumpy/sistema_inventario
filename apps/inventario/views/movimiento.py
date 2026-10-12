# apps/inventario/views/movimiento.py

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from apps.inventario.models import MovimientoStock
from apps.inventario.services.movimiento_service import registrar_entrada_stock
from apps.inventario.serializers import (
    EntradaStockSerializer,
    MovimientoHistorialSerializer
)


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


class MovimientoHistorialAPIView(ListAPIView):
    queryset = (
        MovimientoStock.objects
        .select_related('producto', 'proveedor')
        .filter(proveedor__isnull=False)
        .order_by('-fecha')
    )
    serializer_class = MovimientoHistorialSerializer
    pagination_class = None

