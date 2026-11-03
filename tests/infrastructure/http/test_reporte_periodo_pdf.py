# tests/infrastructure/http/test_reporte_periodo_pdf.py
"""
Test de integración de:
    GET /api/inventario/reportes/pdf/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD

No usa mocks: crea datos reales en la BD de test, autentica con un JWT
real y verifica que la respuesta sea un PDF de verdad.
"""

from datetime import datetime

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.inventario.models import Categoria, MovimientoStock, Producto
from apps.usuarios.models import AdministradorORM


URL_REPORTE_PDF = "/api/inventario/reportes/pdf/"


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def api_client() -> APIClient:
    admin = AdministradorORM.objects.create(
        username="admin_reporte_pdf",
        email="admin_reporte_pdf@test.com",
        password=make_password("clave-de-test"),
        activo="activo",
    )

    client = APIClient()
    token = AccessToken.for_user(admin)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def datos_del_reporte(administrador):
    categoria = Categoria.objects.create(nombre="Frenos PDF Test")

    producto_a = Producto.objects.create(
        nombre="Producto A PDF",
        categoria=categoria,
        precio_unitario="1000.00",
        stock_minimo=1,
        activo=True,
        administrador=administrador,
    )
    producto_b = Producto.objects.create(
        nombre="Producto B PDF",
        categoria=categoria,
        precio_unitario="2000.00",
        stock_minimo=1,
        activo=True,
        administrador=administrador,
    )

    def movimiento(producto, tipo, motivo, cantidad, fecha, canal=None):
        mov = MovimientoStock.objects.create(
            producto=producto,
            tipo=tipo,
            motivo=motivo,
            cantidad=cantidad,
            canal_venta=canal,
            detalle=f"Movimiento {motivo} del test",
        )
        MovimientoStock.objects.filter(pk=mov.pk).update(fecha=fecha)

    fecha = timezone.make_aware(datetime(2026, 10, 15, 12, 0))

    movimiento(producto_a, MovimientoStock.TIPO_ENTRADA, MovimientoStock.MOTIVO_INICIAL, 100, fecha)
    movimiento(producto_b, MovimientoStock.TIPO_ENTRADA, MovimientoStock.MOTIVO_INICIAL, 100, fecha)

    movimiento(
        producto_a, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        30, fecha, canal="whatsapp",
    )
    movimiento(
        producto_b, MovimientoStock.TIPO_SALIDA, MovimientoStock.MOTIVO_VENTA,
        10, fecha, canal="presencial",
    )

    return {
        "producto_a": producto_a,
        "producto_b": producto_b,
    }


# =========================================================================
# GET: PDF real del reporte
# =========================================================================

@pytest.mark.django_db
def test_get_devuelve_un_pdf_real(api_client, datos_del_reporte):
    """
    Si falla: el endpoint no devuelve un PDF válido.
    """

    parametros = {
        "desde": "2026-10-01",
        "hasta": "2026-10-31",
    }

    response = api_client.get(URL_REPORTE_PDF, parametros)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert "attachment" in response["Content-Disposition"]
    assert "reporte_2026-10-01_2026-10-31.pdf" in response["Content-Disposition"]

    contenido = response.content

    # Un PDF real empieza con %PDF- y termina con %%EOF
    assert contenido.startswith(b"%PDF-")
    assert b"%%EOF" in contenido[-1024:]
    assert len(contenido) > 1000


@pytest.mark.django_db
def test_get_sin_fechas_devuelve_400(api_client):
    """
    Si falla: el endpoint genera un PDF sin rango de fechas.
    """

    response = api_client.get(URL_REPORTE_PDF)

    assert response.status_code == 400
