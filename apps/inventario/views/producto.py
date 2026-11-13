# apps/inventario/views/producto.py
from rest_framework.generics import (
    UpdateAPIView,
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView
)

from rest_framework.views import APIView, Response
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import Sum, Q, F, Value, IntegerField
from django.db.models.functions import Coalesce
 
from apps.inventario.models import Producto, MovimientoStock
from apps.inventario.services.reportes import productos_vendidos_en_rango
from apps.inventario.utils.fechas import _parse_fechas
from apps.inventario.serializers import (
    ProductoCreateSerializer,
    ProductoSelectSerializer,
    MovimientoHistorialMovimientoSerializer,
    ProductoSelectNameSerializer,
    ProductoMasVendidoSerializer,
    ProductoVendidoEnRangoSerializer,
)


class ProductoInsertAPIView(CreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoCreateSerializer


class ProductoUpdateAPIView(RetrieveUpdateDestroyAPIView):
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
    serializer_class = MovimientoHistorialMovimientoSerializer
    pagination_class = None

    def get_queryset(self):
        limite = self.kwargs.get('limite')
        qs = MovimientoStock.objects.select_related('producto', 'proveedor').order_by('-fecha')

        if limite is not None:
            limite = min(int(limite), 100)  # techo opcional
            qs = qs[:limite]

        return qs

class ProductosMasVendidosView(ListAPIView):
    serializer_class = ProductoMasVendidoSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Producto.objects
            .annotate(
                cantidad_vendida=Sum(
                    'movimientos__cantidad',
                    filter=Q(
                        movimientos__tipo=MovimientoStock.TIPO_SALIDA,
                        movimientos__motivo=MovimientoStock.MOTIVO_VENTA,
                    ),
                ),
            )
            .filter(cantidad_vendida__gt=0)
            .order_by('-cantidad_vendida', 'nombre')
        )


class ProductosVendidosEnRangoView(generics.ListAPIView):
    serializer_class = ProductoVendidoEnRangoSerializer
    pagination_class = None

    def get_queryset(self):
        desde = self.request.query_params.get("desde")
        hasta = self.request.query_params.get("hasta")

        if not desde or not hasta:
            raise ValidationError({
                "detail": "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."
            })

        return (
            Producto.objects
            .annotate(
                cantidad_vendida=Sum(
                    'movimientos__cantidad',
                    filter=Q(
                        movimientos__tipo=MovimientoStock.TIPO_SALIDA,
                        movimientos__motivo=MovimientoStock.MOTIVO_VENTA,
                        movimientos__fecha__date__gte=desde,
                        movimientos__fecha__date__lte=hasta,
                    ),
                ),
            )
            .filter(cantidad_vendida__gt=0)
            .order_by('-cantidad_vendida', 'nombre')
        )


class ProductosVendidosEnRangoView(generics.ListAPIView):
    serializer_class = ProductoVendidoEnRangoSerializer

    def get_queryset(self):
        desde, hasta = _parse_fechas(self.request)
        return productos_vendidos_en_rango(desde, hasta)
