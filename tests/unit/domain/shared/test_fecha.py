# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para Fecha (shared)"""

import pytest
from datetime import datetime, timezone, timedelta
from core.domain.shared.fecha import Fecha


class TestFecha:
    def test_crear_fecha_utc(self):
        dt = datetime.now(timezone.utc)
        f = Fecha(dt)
        assert f.valor == dt

    def test_fecha_sin_timezone_se_normaliza_a_utc(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        f = Fecha(dt)
        assert f.valor.tzinfo == timezone.utc
        assert f.valor.hour == 12

    def test_fecha_con_timezone_no_utc_se_convierte(self):
        tz = timezone(timedelta(hours=-3))
        dt = datetime(2024, 1, 1, 15, 0, 0, tzinfo=tz)
        f = Fecha(dt)
        assert f.valor.tzinfo == timezone.utc
        assert f.valor.hour == 18  # 15 - (-3) = 18 UTC

    def test_ahora_crea_fecha_actual(self):
        f = Fecha.ahora()
        assert f.valor.tzinfo == timezone.utc

    def test_desde_iso(self):
        f = Fecha.desde_iso("2024-06-15T10:30:00+00:00")
        assert f.valor.year == 2024
        assert f.valor.month == 6
        assert f.valor.day == 15
        assert f.valor.hour == 10

    def test_a_iso(self):
        f = Fecha.desde_iso("2024-06-15T10:30:00+00:00")
        assert "2024-06-15T10:30:00" in f.a_iso()

    def test_es_antes_de(self):
        f1 = Fecha.desde_iso("2024-01-01T00:00:00+00:00")
        f2 = Fecha.desde_iso("2024-06-15T00:00:00+00:00")
        assert f1.es_antes_de(f2) is True
        assert f2.es_antes_de(f1) is False

    def test_es_despues_de(self):
        f1 = Fecha.desde_iso("2024-01-01T00:00:00+00:00")
        f2 = Fecha.desde_iso("2024-06-15T00:00:00+00:00")
        assert f2.es_despues_de(f1) is True
        assert f1.es_despues_de(f2) is False

    def test_fechas_iguales(self):
        f1 = Fecha.desde_iso("2024-01-01T00:00:00+00:00")
        f2 = Fecha.desde_iso("2024-01-01T00:00:00+00:00")
        assert f1 == f2
        assert hash(f1) == hash(f2)

    def test_inmutable(self):
        f = Fecha.ahora()
        with pytest.raises(Exception):
            f.valor = datetime.now(timezone.utc)