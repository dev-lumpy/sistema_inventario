 # apps/inventario/views/resumen.py
from datetime import date
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.inventario.models import MovimientoStock


class ResumenHoyAPIView(APIView):
    def get(self, request):
        hoy = date.today()
        movs = MovimientoStock.objects.filter(fecha__date=hoy)

        entradas = movs.filter(tipo='E').aggregate(t=Sum('cantidad'))['t'] or 0
        salidas  = movs.filter(tipo='S').aggregate(t=Sum('cantidad'))['t'] or 0

        return Response({
            'ventas': salidas,
            'entradas': entradas,
        })


class ResumenPeriodoAPIView(APIView):
    def get(self, request):
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        if not desde or not hasta:
            raise ValidationError({
                'detail': "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."
            })

        movs = MovimientoStock.objects.filter(
            fecha__date__gte=desde,
            fecha__date__lte=hasta,
        )

        entradas = movs.filter(tipo=MovimientoStock.TIPO_ENTRADA).aggregate(t=Sum('cantidad'))['t'] or 0
        salidas = movs.filter(tipo=MovimientoStock.TIPO_SALIDA).aggregate(t=Sum('cantidad'))['t'] or 0

        return Response({
            'desde': desde,
            'hasta': hasta,
            'entradas': entradas,
            'salidas': salidas,
        })
