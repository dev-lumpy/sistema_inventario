# pyright: reportAttributeAccessIssue=false
"""Pruebas para los casos de uso de movimiento de stock"""

import pytest
from core.application.movimiento_stock.registrar_entrada_stock import (
    RegistrarEntradaStock,
    RegistrarEntradaStockInput,
)
from core.application.movimiento_stock.registrar_salida_stock import (
    RegistrarSalidaStock,
    RegistrarSalidaStockInput,
)
from core.application.producto.registrar_producto import (
    RegistrarProducto,
    RegistrarProductoInput,
)
from core.adapters import (
    ProductoRepositoryMemoria,
    ProveedorRepositoryMemoria,
    MovimientoStockRepositoryMemoria,
)
from core.domain.proveedor import Proveedor, ProveedorId, NombreProveedor
from core.domain.producto.exceptions import ProductoNoEncontradoException


class TestRegistrarEntradaStock:
    def test_entrada_exitosa(self):
        prod_repo = ProductoRepositoryMemoria()
        prov_repo = ProveedorRepositoryMemoria()
        mov_repo = MovimientoStockRepositoryMemoria()

        # Registrar producto
        registrar_prod = RegistrarProducto(prod_repo)
        prod_output = registrar_prod.ejecutar(RegistrarProductoInput(
            nombre="Laptop", precio=1000, cantidad_inicial=10, stock_minimo=2,
        ))
        producto_id = prod_output.producto_id

        # Registrar proveedor
        proveedor = Proveedor(
            id=ProveedorId.generar(),
            nombre=NombreProveedor("Distribuidora XYZ"),
        )
        prov_repo.guardar(proveedor)

        # Ejecutar entrada
        use_case = RegistrarEntradaStock(prod_repo, prov_repo, mov_repo)
        output = use_case.ejecutar(RegistrarEntradaStockInput(
            producto_id=producto_id,
            cantidad=20,
            proveedor_id=str(proveedor.id),
        ))

        assert output.movimiento_id is not None
        producto = prod_repo.obtener_por_nombre("Laptop")
        assert producto is not None
        assert producto.cantidad.valor == 30  # 10 + 20

        movimientos = mov_repo.listar_por_producto(producto.id)
        assert len(movimientos) == 1

    def test_entrada_producto_inexistente(self):
        prod_repo = ProductoRepositoryMemoria()
        prov_repo = ProveedorRepositoryMemoria()
        mov_repo = MovimientoStockRepositoryMemoria()

        use_case = RegistrarEntradaStock(prod_repo, prov_repo, mov_repo)
        with pytest.raises(ProductoNoEncontradoException):
            use_case.ejecutar(RegistrarEntradaStockInput(
                producto_id="00000000-0000-0000-0000-000000000000",
                cantidad=10,
                proveedor_id="00000000-0000-0000-0000-000000000001",
            ))


class TestRegistrarSalidaStock:
    def test_salida_exitosa(self):
        prod_repo = ProductoRepositoryMemoria()
        mov_repo = MovimientoStockRepositoryMemoria()

        registrar_prod = RegistrarProducto(prod_repo)
        prod_output = registrar_prod.ejecutar(RegistrarProductoInput(
            nombre="Laptop", precio=1000, cantidad_inicial=10, stock_minimo=2,
        ))
        producto_id = prod_output.producto_id

        use_case = RegistrarSalidaStock(prod_repo, mov_repo)
        output = use_case.ejecutar(RegistrarSalidaStockInput(
            producto_id=producto_id,
            cantidad=3,
            canal_venta="whatsapp",
        ))

        assert output.movimiento_id is not None
        producto = prod_repo.obtener_por_nombre("Laptop")
        assert producto is not None
        assert producto.cantidad.valor == 7  # 10 - 3

    def test_salida_stock_insuficiente(self):
        prod_repo = ProductoRepositoryMemoria()
        mov_repo = MovimientoStockRepositoryMemoria()

        registrar_prod = RegistrarProducto(prod_repo)
        prod_output = registrar_prod.ejecutar(RegistrarProductoInput(
            nombre="Laptop", precio=1000, cantidad_inicial=5, stock_minimo=1,
        ))
        producto_id = prod_output.producto_id

        use_case = RegistrarSalidaStock(prod_repo, mov_repo)
        with pytest.raises(Exception):
            use_case.ejecutar(RegistrarSalidaStockInput(
                producto_id=producto_id,
                cantidad=100,
                canal_venta="whatsapp",
            ))