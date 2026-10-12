 # apps/inventario/views/resumen.py
from datetime import date
from django.db.models import Sum
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
