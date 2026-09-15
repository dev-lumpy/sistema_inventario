# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para la entidad MovimientoStock"""

import pytest
from core.domain.movimiento_stock.movimiento_stock import MovimientoStock
from core.domain.movimiento_stock.value_objects import MovimientoId
from core.domain.movimiento_stock.tipo_movimiento import TipoMovimiento
from core.domain.movimiento_stock.canal_venta import CanalVenta
from core.domain.movimiento_stock.exceptions import (
    ProveedorRequeridoParaEntradaException,
    CanalRequeridoParaSalidaException,
)
from core.domain.producto.value_objects import ProductoId
from core.domain.proveedor.value_objects import ProveedorId
from core.domain.shared.cantidad import Cantidad
from core.domain.shared.fecha import Fecha


class TestMovimientoStockCreacion:
    def _prod_id(self):
        return ProductoId.generar()

    def _prov_id(self):
        return ProveedorId.generar()

    def test_crear_entrada_valida(self):
        m = MovimientoStock.entrada(
            producto_id=self._prod_id(),
            cantidad=Cantidad(50),
            proveedor_id=self._prov_id(),
        )
        assert m.tipo == TipoMovimiento.ENTRADA
        assert m.cantidad.valor == 50
        assert m.proveedor_id is not None
        assert m.canal_venta is None
        assert m.fecha is not None

    def test_crear_salida_valida(self):
        m = MovimientoStock.salida(
            producto_id=self._prod_id(),
            cantidad=Cantidad(10),
            canal_venta=CanalVenta.WHATSAPP,
        )
        assert m.tipo == TipoMovimiento.SALIDA
        assert m.cantidad.valor == 10
        assert m.canal_venta == CanalVenta.WHATSAPP
        assert m.proveedor_id is None

    def test_salida_sin_canal_lanza_excepcion(self):
        with pytest.raises(CanalRequeridoParaSalidaException):
            MovimientoStock.salida(
                producto_id=self._prod_id(),
                cantidad=Cantidad(10),
                canal_venta=None,
            )

    def test_entrada_sin_proveedor_lanza_excepcion(self):
        with pytest.raises(ProveedorRequeridoParaEntradaException):
            MovimientoStock.entrada(
                producto_id=self._prod_id(),
                cantidad=Cantidad(10),
                proveedor_id=None,
            )

    def test_entrada_con_canal_venta_lanza_error(self):
        with pytest.raises(ValueError):
            MovimientoStock(
                id=MovimientoId.generar(),
                producto_id=self._prod_id(),
                tipo=TipoMovimiento.ENTRADA,
                cantidad=Cantidad(10),
                proveedor_id=self._prov_id(),
                canal_venta=CanalVenta.WHATSAPP,
            )

    def test_salida_con_proveedor_lanza_error(self):
        with pytest.raises(ValueError):
            MovimientoStock(
                id=MovimientoId.generar(),
                producto_id=self._prod_id(),
                tipo=TipoMovimiento.SALIDA,
                cantidad=Cantidad(10),
                canal_venta=CanalVenta.PRESENCIAL,
                proveedor_id=self._prov_id(),
            )

    def test_cantidad_cero_lanza_error(self):
        with pytest.raises(ValueError):
            MovimientoStock.entrada(
                producto_id=self._prod_id(),
                cantidad=Cantidad(0),
                proveedor_id=self._prov_id(),
            )


class TestMovimientoStockIdentidad:
    def test_igualdad_por_id(self):
        id = MovimientoId.generar()
        pid = ProductoId.generar()
        m1 = MovimientoStock(
            id=id,
            producto_id=pid,
            tipo=TipoMovimiento.ENTRADA,
            cantidad=Cantidad(10),
            proveedor_id=ProveedorId.generar(),
        )
        m2 = MovimientoStock(
            id=id,
            producto_id=pid,
            tipo=TipoMovimiento.SALIDA,
            cantidad=Cantidad(5),
            canal_venta=CanalVenta.OTRO,
        )
        assert m1 == m2
        assert hash(m1) == hash(m2)

    def test_distintos_id_son_distintos(self):
        pid = ProductoId.generar()
        m1 = MovimientoStock.entrada(
            producto_id=pid, cantidad=Cantidad(10), proveedor_id=ProveedorId.generar()
        )
        m2 = MovimientoStock.entrada(
            producto_id=pid, cantidad=Cantidad(10), proveedor_id=ProveedorId.generar()
        )
        assert m1 != m2


class TestMovimientoStockCanales:
    def test_todos_los_canales_son_validos(self):
        pid = ProductoId.generar()
        for canal in CanalVenta:
            m = MovimientoStock.salida(
                producto_id=pid,
                cantidad=Cantidad(1),
                canal_venta=canal,
            )
            assert m.canal_venta == canal

    def test_tipos_de_movimiento(self):
        assert TipoMovimiento.ENTRADA.value == "entrada"
        assert TipoMovimiento.SALIDA.value == "salida"