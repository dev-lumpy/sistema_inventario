# apps/inventario/pdf/reporte_periodo.py
from django.template.loader import render_to_string


def generar_pdf_reporte(desde, hasta, resumen, productos):
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError(
            'La exportacion a PDF no esta disponible: falta WeasyPrint '
            'o sus dependencias del sistema.'
        ) from exc

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
