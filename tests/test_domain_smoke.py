from __future__ import annotations

import unittest
from decimal import Decimal

from core.domain.accounts.entities import VinculoVendedorAdministrador
from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.catalog.entities import Categoria, MovimientoInventario, Producto
from core.domain.catalog.enums import MotivoMovimiento
from core.domain.catalog.exceptions import CategoriaDeOtroAdministradorError
from core.domain.catalog.value_objects import NombreCategoria, NombreProducto
from core.domain.sales.entities import Venta
from core.domain.sales.exceptions import VentaSinLineasError
from core.domain.shared.enums import TipoCliente
from core.domain.shared.errors import ValidationError
from core.domain.shared.value_objects import Money, Quantity


class MoneyTests(unittest.TestCase):
    def test_multiplica_precio_por_cantidad(self) -> None:
        precio = Money.desde("12.50")
        cantidad = Quantity.desde("3")
        self.assertEqual((precio * cantidad).amount, Decimal("37.50"))

    def test_rechaza_montos_negativos(self) -> None:
        with self.assertRaises(ValidationError):
            Money.desde("-1")


class AccountsTests(unittest.TestCase):
    def test_vinculo_pendiente_no_puede_vender(self) -> None:
        vinculo = VinculoVendedorAdministrador(
            vendedor_id=1,
            administrador_id=2,
            solicitado_por=SolicitadoPor.VENDEDOR,
        )
        self.assertFalse(vinculo.puede_vender())
        vinculo.aceptar()
        self.assertEqual(vinculo.estado, EstadoVinculo.ACEPTADO)
        self.assertTrue(vinculo.puede_vender())


class CatalogTests(unittest.TestCase):
    def test_producto_no_acepta_categoria_de_otro_admin(self) -> None:
        producto = Producto(
            administrador_id=1,
            categoria_id=10,
            nombre=NombreProducto("Cemento"),
        )
        categoria = Categoria(
            administrador_id=2,
            nombre=NombreCategoria("Materiales"),
            id=10,
        )
        with self.assertRaises(CategoriaDeOtroAdministradorError):
            producto.cambiar_categoria(categoria)

    def test_signo_de_movimientos(self) -> None:
        salida = MovimientoInventario(
            administrador_id=1,
            producto_id=2,
            motivo=MotivoMovimiento.VENTA,
            cantidad=Quantity.desde("2"),
            usuario_id=3,
        )
        entrada = MovimientoInventario(
            administrador_id=1,
            producto_id=2,
            motivo=MotivoMovimiento.COMPRA,
            cantidad=Quantity.desde("5"),
            usuario_id=3,
        )
        self.assertEqual(salida.signo, -1)
        self.assertEqual(entrada.signo, 1)


class SalesTests(unittest.TestCase):
    def test_venta_calcula_total_y_se_confirma(self) -> None:
        venta = Venta(
            administrador_id=1,
            vendedor_id=2,
            tipo_cliente=TipoCliente.MAYOREO,
        )
        venta.agregar_linea(10, Quantity.desde("2"), Money.desde("50"))
        venta.agregar_linea(11, Quantity.desde("1"), Money.desde("25.50"))
        self.assertEqual(venta.total.amount, Decimal("125.50"))
        venta.confirmar()
        self.assertTrue(venta.esta_confirmada)

    def test_venta_sin_lineas_no_se_confirma(self) -> None:
        venta = Venta(
            administrador_id=1,
            vendedor_id=2,
            tipo_cliente=TipoCliente.INDIVIDUAL,
        )
        with self.assertRaises(VentaSinLineasError):
            venta.confirmar()


if __name__ == "__main__":
    unittest.main()
