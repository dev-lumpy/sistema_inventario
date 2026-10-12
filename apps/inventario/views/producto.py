# apps/inventario/views/producto.py
from rest_framework.generics import UpdateAPIView, CreateAPIView, ListAPIView
from rest_framework.views import APIView, Response
from django.db.models import Sum, Q, F, Value, IntegerField
from django.db.models.functions import Coalesce
 
from apps.inventario.models import Producto, MovimientoStock
from apps.inventario.serializers import (
    ProductoCreateSerializer,
    ProductoSelectSerializer,
    MovimientoHistorialMovimientoSerializer,
    ProductoSelectNameSerializer
)


class ProductoInsertAPIView(CreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoCreateSerializer


class ProductoUpdateAPIView(UpdateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoCreateSerializer
    lookup_field = 'pk'


class ProductoSelectAPIView(ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSelectSerializer
    pagination_class = None


class ProductoSelectNameAPIView(ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSelectNameSerializer
    pagination_class = None 



class ProductoAlertStockAPIView(APIView):
    def get(self, request):
        # 1. Calcular stock_actual en SQL (una sola query, sin N+1)
        productos = Producto.objects.filter(activo=True).annotate(
            stock=Coalesce(
                Sum('movimientos__cantidad', filter=Q(movimientos__tipo='E')),
                Value(0),
            ) - Coalesce(
                Sum('movimientos__cantidad', filter=Q(movimientos__tipo='S')),
                Value(0),
            ),
        )

        # 2. Filtrar los que están en alerta
        productos = productos.filter(stock__lte=F('stock_minimo'))

        # 3. Devolver solo los campos que querés
        data = list(productos.values('id', 'nombre', 'stock', 'stock_minimo'))

        return Response(data)


class ProductoHistoryMovimientosAPIView(ListAPIView):
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoHistorialMovimientoSerializer
    pagination_class = None

