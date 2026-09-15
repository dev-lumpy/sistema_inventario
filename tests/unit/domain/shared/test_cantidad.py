# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para Cantidad (shared)"""

import pytest
from core.domain.shared.cantidad import Cantidad, CantidadInvalidaError, StockInsuficienteError


class TestCantidad:
    def test_crear_cantidad_valida(self):
        c = Cantidad(10)
        assert c.valor == 10

    def test_crear_cantidad_cero(self):
        c = Cantidad(0)
        assert c.valor == 0

    def test_crear_cantidad_negativa_lanza_error(self):
        with pytest.raises(CantidadInvalidaError):
            Cantidad(-5)

    def test_sumar_cantidad_positiva(self):
        c = Cantidad(10).sumar(5)
        assert c.valor == 15

    def test_sumar_cantidad_negativa_lanza_error(self):
        c = Cantidad(10)
        with pytest.raises(CantidadInvalidaError):
            c.sumar(-5)

    def test_restar_cantidad_positiva(self):
        c = Cantidad(10).restar(3)
        assert c.valor == 7

    def test_restar_mas_de_lo_disponible_lanza_error(self):
        with pytest.raises(StockInsuficienteError) as exc:
            Cantidad(5).restar(10)
        assert exc.value.disponible == 5
        assert exc.value.solicitado == 10

    def test_es_menor_que(self):
        assert Cantidad(5).es_menor_que(Cantidad(10)) is True
        assert Cantidad(10).es_menor_que(Cantidad(5)) is False

    def test_es_mayor_que(self):
        assert Cantidad(10).es_mayor_que(Cantidad(5)) is True
        assert Cantidad(5).es_mayor_que(Cantidad(10)) is False

    def test_es_cero(self):
        assert Cantidad(0).es_cero() is True
        assert Cantidad(5).es_cero() is False

    def test_es_positivo(self):
        assert Cantidad(5).es_positivo() is True
        assert Cantidad(0).es_positivo() is False

    def test_inmutable(self):
        c = Cantidad(10)
        with pytest.raises(Exception):
            c.valor = 5


class TestCantidadInvalidaError:
    def test_es_subclase_de_value_error(self):
        assert issubclass(CantidadInvalidaError, ValueError)


class TestStockInsuficienteError:
    def test_es_subclase_de_value_error(self):
        assert issubclass(StockInsuficienteError, ValueError)

    def test_contiene_disponible_y_solicitado(self):
        e = StockInsuficienteError(5, 10)
        assert e.disponible == 5
        assert e.solicitado == 10