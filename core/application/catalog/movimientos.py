from __future__ import annotations

from decimal import Decimal

from core.application.ports.unit_of_work import UnitOfWork
from core.domain.accounts.entities import Vendedor, VinculoVendedorAdministrador
from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.accounts.exceptions import VinculoNoAceptadoError
from core.domain.catalog.entities import MovimientoInventario
from core.domain.catalog.enums import MotivoMovimiento, ReferenciaTipo
from core.domain.catalog.exceptions import (
    PrecioNoVigenteError,
    ProductoDeOtroAdministradorError,
)
from core.domain.catalog.services import verificar_stock_suficiente
from core.domain.purchases.entities import Compra
from core.domain.sales.entities import Venta
from core.domain.sales.enums import CanalVenta
from core.domain.shared.enums import TipoCliente
from core.domain.shared.errors import (
    BusinessRuleViolation,
    NotFoundError,
    ValidationError,
)
from core.domain.shared.value_objects import Money, Quantity


class RegistrarEntrada:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        administrador_id: int,
        usuario_id: int,
        producto_id: int,
        proveedor_id: int,
        cantidad,
        costo_unitario=0,
    ):
        producto = self._uow.productos.obtener_por_id(producto_id)
        if producto is None:
            raise NotFoundError("El producto no existe")
        if not producto.pertenece_a(administrador_id):
            raise ProductoDeOtroAdministradorError(producto_id, administrador_id)

        proveedor = self._uow.proveedores.obtener_por_id(proveedor_id)
        if proveedor is None:
            raise NotFoundError("El proveedor no existe")
        proveedor.verificar_administrador(administrador_id)

        administrador = self._uow.administradores.obtener_por_id(administrador_id)
        moneda = administrador.moneda.valor if administrador else "BOB"

        compra = Compra(
            administrador_id=administrador_id,
            proveedor_id=proveedor_id,
            usuario_id=usuario_id,
            moneda=moneda,
            nota="Entrada de stock",
        )
        compra.agregar_linea(
            producto_id=producto_id,
            cantidad=Quantity(Decimal(str(cantidad))),
            costo_unitario=Money(Decimal(str(costo_unitario or 0)), moneda),
            administrador_id=administrador_id,
        )
        self._uow.compras.guardar(compra)
        compra.confirmar(proveedor)
        self._uow.compras.guardar(compra)

        stock = self._uow.movimientos.calcular_stock(producto_id, administrador_id)
        return compra, stock


class RegistrarVenta:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        administrador_id: int,
        vendedor_id: int,
        items: list[dict],
        canal_venta: str,
    ):
        if not items:
            raise ValidationError("Agregá al menos un producto a la venta")

        self._habilitar_vendedor(administrador_id, vendedor_id)

        normalizados = []
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError("Cada ítem de la venta debe ser un objeto")
            try:
                producto_id = int(item.get("producto_id") or item.get("producto") or 0)
                cantidad_vo = Quantity(Decimal(str(item.get("cantidad"))))
            except Exception as exc:
                raise ValidationError("Producto o cantidad inválidos") from exc

            producto = self._uow.productos.obtener_por_id(producto_id)
            if producto is None:
                raise NotFoundError("El producto no existe")
            if not producto.pertenece_a(administrador_id):
                raise ProductoDeOtroAdministradorError(producto_id, administrador_id)

            precio = self._uow.precios.obtener_vigente(
                producto_id, administrador_id, TipoCliente.INDIVIDUAL
            )
            if precio is None:
                raise PrecioNoVigenteError(producto_id, TipoCliente.INDIVIDUAL.value)
            normalizados.append((producto_id, cantidad_vo, precio))

        requeridos: dict[int, Decimal] = {}
        for producto_id, cantidad_vo, _ in normalizados:
            requeridos[producto_id] = (
                requeridos.get(producto_id, Decimal("0")) + cantidad_vo.value
            )

        for producto_id, cantidad_total in requeridos.items():
            stock_actual = self._uow.movimientos.calcular_stock(
                producto_id, administrador_id
            )
            verificar_stock_suficiente(
                producto_id, stock_actual, Quantity(cantidad_total)
            )

        moneda = normalizados[0][2].precio.currency
        venta = Venta(
            administrador_id=administrador_id,
            vendedor_id=vendedor_id,
            tipo_cliente=TipoCliente.INDIVIDUAL,
            canal_venta=CanalVenta.desde(canal_venta),
            moneda=moneda,
        )
        for producto_id, cantidad_vo, precio in normalizados:
            venta.agregar_linea(
                producto_id=producto_id,
                cantidad=cantidad_vo,
                precio_unitario=precio.precio,
                administrador_id=administrador_id,
            )

        self._uow.ventas.guardar(venta)
        venta.confirmar()
        self._uow.ventas.guardar(venta)

        stocks = {
            producto_id: self._uow.movimientos.calcular_stock(
                producto_id, administrador_id
            )
            for producto_id in requeridos
        }
        return venta, stocks

    def _habilitar_vendedor(self, administrador_id: int, vendedor_id: int) -> Vendedor:
        vendedor = self._uow.vendedores.obtener_por_id(vendedor_id)
        if vendedor is None:
            vendedor = self._habilitar_administrador_como_vendedor(
                administrador_id, vendedor_id
            )
        vendedor.verificar_puede_operar()

        vinculo = self._uow.vinculos.obtener(vendedor_id, administrador_id)
        if vinculo is None:
            raise VinculoNoAceptadoError(vendedor_id, administrador_id, "inexistente")
        vinculo.verificar_puede_vender(vendedor.bloqueado)
        return vendedor

    def _habilitar_administrador_como_vendedor(
        self, administrador_id: int, usuario_id: int
    ) -> Vendedor:
        if administrador_id != usuario_id:
            raise NotFoundError("El vendedor no existe")
        administrador = self._uow.administradores.obtener_por_id(administrador_id)
        if administrador is None:
            raise NotFoundError("El vendedor no existe")

        vendedor = Vendedor(
            usuario=administrador.usuario,
            creado_por_admin_id=administrador_id,
        )
        self._uow.vendedores.guardar(vendedor)
        self._uow.vinculos.guardar(
            VinculoVendedorAdministrador(
                vendedor_id=usuario_id,
                administrador_id=administrador_id,
                estado=EstadoVinculo.ACEPTADO,
                solicitado_por=SolicitadoPor.ADMIN,
            )
        )
        return vendedor


class RegistrarSalida:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        administrador_id: int,
        vendedor_id: int,
        producto_id: int,
        cantidad,
        canal_venta: str,
    ):
        venta, stocks = RegistrarVenta(self._uow).ejecutar(
            administrador_id=administrador_id,
            vendedor_id=vendedor_id,
            items=[{"producto_id": producto_id, "cantidad": cantidad}],
            canal_venta=canal_venta,
        )
        return venta, stocks.get(int(producto_id), Decimal("0"))


class AnularVenta:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self, administrador_id: int, usuario_id: int, venta_id: int
    ) -> Venta:
        venta = self._uow.ventas.obtener_por_id(venta_id)
        if venta is None:
            raise NotFoundError("La venta no existe")
        if venta.administrador_id != administrador_id:
            raise BusinessRuleViolation("La venta pertenece a otro administrador")

        if venta.esta_confirmada:
            for linea in venta.lineas:
                self._uow.movimientos.guardar(
                    MovimientoInventario(
                        administrador_id=administrador_id,
                        producto_id=linea.producto_id,
                        motivo=MotivoMovimiento.DEVOLUCION,
                        cantidad=linea.cantidad,
                        precio_unitario=linea.precio_unitario,
                        usuario_id=usuario_id,
                        referencia_tipo=ReferenciaTipo.VENTA,
                        referencia_id=venta.id,
                        nota="Anulación de venta",
                    )
                )

        venta.anular()
        self._uow.ventas.guardar(venta)
        return venta


class AnularCompra:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self, administrador_id: int, usuario_id: int, compra_id: int
    ) -> Compra:
        compra = self._uow.compras.obtener_por_id(compra_id)
        if compra is None:
            raise NotFoundError("La compra no existe")
        if compra.administrador_id != administrador_id:
            raise BusinessRuleViolation("La compra pertenece a otro administrador")

        if compra.esta_confirmada:
            for linea in compra.lineas:
                self._uow.movimientos.guardar(
                    MovimientoInventario(
                        administrador_id=administrador_id,
                        producto_id=linea.producto_id,
                        motivo=MotivoMovimiento.AJUSTE_NEG,
                        cantidad=linea.cantidad,
                        costo_unitario=linea.costo_unitario,
                        usuario_id=usuario_id,
                        referencia_tipo=ReferenciaTipo.COMPRA,
                        referencia_id=compra.id,
                        nota="Anulación de compra",
                    )
                )

        compra.anular()
        self._uow.compras.guardar(compra)
        return compra
