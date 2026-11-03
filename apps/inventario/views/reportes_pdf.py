# apps/inventario/views/reportes_pdf.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.inventario.services.reportes import (
    productos_vendidos_en_rango,
    resumen_periodo,
)
from apps.inventario.pdf.reporte_periodo import generar_pdf_reporte
from apps.inventario.renderers import PDFRenderer


class ReportePeriodoPDFView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [PDFRenderer]

    def get(self, request):
        desde = request.query_params.get("desde")
        hasta = request.query_params.get("hasta")
        if not desde or not hasta:
            raise ValidationError({"detail": "desde y hasta son obligatorios."})

        productos = list(productos_vendidos_en_rango(desde, hasta))
        resumen = resumen_periodo(desde, hasta)

        pdf_bytes = generar_pdf_reporte(desde, hasta, resumen, productos)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_{desde}_{hasta}.pdf"'
        )
        return response
