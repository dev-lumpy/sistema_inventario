# apps/inventario/pdf/reporte_periodo.py
from django.template.loader import render_to_string
from weasyprint import HTML


def generar_pdf_reporte(desde, hasta, resumen, productos):
    html_string = render_to_string(
        "inventario/reporte_periodo_pdf.html",
        {
            "desde": desde,
            "hasta": hasta,
            "resumen": resumen,
            "productos": productos,
        },
    )
    return HTML(string=html_string).write_pdf() 
