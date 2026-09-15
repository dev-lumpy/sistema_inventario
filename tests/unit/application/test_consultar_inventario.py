# pyright: reportAttributeAccessIssue=false
"""Pruebas para el caso de uso ConsultarInventario"""

from core.application.producto.consultar_inventario import (
    ConsultarInventario,
    ConsultarInventarioInput,
)
from core.application.producto.registrar_producto import (
    RegistrarProducto,
    RegistrarProductoInput,
)
from core.adapters import ProductoRepositoryMemoria


class TestConsultarInventario:
    def test_listar_todos(self):
        repo = ProductoRepositoryMemoria()
        registrar = RegistrarProducto(repo)
        consultar = ConsultarInventario(repo)

        registrar.ejecutar(RegistrarProductoInput(
            nombre="Producto A", precio=10, cantidad_inicial=5, stock_minimo=1
        ))
        registrar.ejecutar(RegistrarProductoInput(
            nombre="Producto B", precio=20, cantidad_inicial=10, stock_minimo=2
        ))

        output = consultar.ejecutar(ConsultarInventarioInput())
        assert len(output.productos) == 2

    def test_filtrar_por_categoria(self):
        repo = ProductoRepositoryMemoria()
        registrar = RegistrarProducto(repo)
        consultar = ConsultarInventario(repo)

        registrar.ejecutar(RegistrarProductoInput(
            nombre="TV LED", precio=500, cantidad_inicial=10, stock_minimo=2,
            categoria_id="Electrónicos",
        ))
        registrar.ejecutar(RegistrarProductoInput(
            nombre="Camisa", precio=30, cantidad_inicial=50, stock_minimo=10,
            categoria_id="Ropa",
        ))

        output = consultar.ejecutar(ConsultarInventarioInput(categoria_id="Ropa"))
        assert len(output.productos) == 1
        assert output.productos[0].nombre.valor == "Camisa"

    def test_buscar_por_texto(self):
        repo = ProductoRepositoryMemoria()
        registrar = RegistrarProducto(repo)
        consultar = ConsultarInventario(repo)

        registrar.ejecutar(RegistrarProductoInput(
            nombre="Laptop Gamer", precio=1000, cantidad_inicial=5, stock_minimo=1,
        ))
        registrar.ejecutar(RegistrarProductoInput(
            nombre="Mouse Pad", precio=15, cantidad_inicial=20, stock_minimo=5,
        ))

        output = consultar.ejecutar(ConsultarInventarioInput(texto="laptop"))
        assert len(output.productos) == 1
        assert "Laptop" in output.productos[0].nombre.valor