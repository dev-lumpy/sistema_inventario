# pyright: reportAttributeAccessIssue=false
"""Pruebas para el caso de uso RegistrarProducto"""

import pytest
from core.application.producto.registrar_producto import (
    RegistrarProducto,
    RegistrarProductoInput,
)
from core.adapters import ProductoRepositoryMemoria


class TestRegistrarProducto:
    def test_registrar_producto_exitoso(self):
        repo = ProductoRepositoryMemoria()
        use_case = RegistrarProducto(repo)

        output = use_case.ejecutar(RegistrarProductoInput(
            nombre="Laptop HP",
            precio=1500.00,
            cantidad_inicial=50,
            stock_minimo=10,
            categoria_id="Electrónicos",
        ))

        assert output.producto_id is not None
        assert len(repo.listar_todos()) == 1

        producto = repo.listar_todos()[0]
        assert producto.nombre.valor == "Laptop HP"
        assert producto.precio.valor == 1500.00
        assert producto.cantidad.valor == 50
        assert producto.categoria_id == "Electrónicos"

    def test_registrar_producto_sin_categoria(self):
        repo = ProductoRepositoryMemoria()
        use_case = RegistrarProducto(repo)

        output = use_case.ejecutar(RegistrarProductoInput(
            nombre="Teclado Mecánico",
            precio=89.99,
            cantidad_inicial=20,
            stock_minimo=5,
        ))

        producto = repo.obtener_por_nombre("Teclado Mecánico")
        assert producto is not None
        assert producto.categoria_id is None