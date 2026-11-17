from __future__ import annotations

from decimal import Decimal

from core.application.ports.unit_of_work import UnitOfWork
from core.domain.catalog.entities import (
    Categoria,
    MovimientoInventario,
    PrecioProducto,
    Producto,
)
from core.domain.catalog.exceptions import (
    CategoriaDeOtroAdministradorError,
    ProductoDeOtroAdministradorError,
)
from core.domain.catalog.value_objects import (
    NombreCategoria,
    NombreProducto,
    StockMinimo,
)
from core.domain.purchases.entities import Proveedor
from core.domain.shared.enums import TipoCliente
from core.domain.shared.errors import NotFoundError
from core.domain.shared.validators import texto_opcional, texto_requerido
from core.domain.shared.value_objects import Money, Quantity


def _precio(valor, moneda: str = "BOB") -> Money:
    return Money(Decimal(str(valor or 0)), moneda)


class GestionarCategoria:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def crear(self, administrador_id: int, nombre: str) -> Categoria:
        categoria = Categoria(
            administrador_id=administrador_id,
            nombre=NombreCategoria(nombre),
        )
        return self._uow.categorias.guardar(categoria)

    def actualizar(
        self, administrador_id: int, categoria_id: int, nombre: str
    ) -> Categoria:
        categoria = self._uow.categorias.obtener_por_id(categoria_id)
        if categoria is None:
            raise NotFoundError("La categoría no existe")
        if not categoria.pertenece_a(administrador_id):
            raise CategoriaDeOtroAdministradorError(categoria_id, administrador_id)
        categoria.renombrar(NombreCategoria(nombre))
        return self._uow.categorias.guardar(categoria)

    def eliminar(self, administrador_id: int, categoria_id: int) -> None:
        categoria = self._uow.categorias.obtener_por_id(categoria_id)
        if categoria is None:
            raise NotFoundError("La categoría no existe")
        if not categoria.pertenece_a(administrador_id):
            raise CategoriaDeOtroAdministradorError(categoria_id, administrador_id)
        self._uow.categorias.eliminar(categoria_id)


class GestionarProducto:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def crear(
        self,
        administrador_id: int,
        usuario_id: int,
        nombre: str,
        categoria_id: int,
        precio,
        stock_minimo=0,
        cantidad_inicial=0,
    ) -> Producto:
        categoria = self._uow.categorias.obtener_por_id(categoria_id)
        if categoria is None:
            raise NotFoundError("La categoría no existe")
        if not categoria.pertenece_a(administrador_id):
            raise CategoriaDeOtroAdministradorError(categoria_id, administrador_id)

        producto = Producto(
            administrador_id=administrador_id,
            categoria_id=categoria_id,
            nombre=NombreProducto(nombre),
            stock_minimo=StockMinimo(Decimal(str(stock_minimo or 0))),
        )
        self._uow.productos.guardar(producto)
        self._fijar_precio_individual(administrador_id, producto, precio)

        cantidad = Decimal(str(cantidad_inicial or 0))
        if cantidad > 0:
            self._uow.movimientos.guardar(
                MovimientoInventario.ajuste(
                    administrador_id=administrador_id,
                    producto_id=producto.id or 0,
                    cantidad=Quantity(cantidad),
                    usuario_id=usuario_id,
                    positivo=True,
                    nota="Stock inicial",
                )
            )
        return producto

    def actualizar(
        self,
        administrador_id: int,
        producto_id: int,
        nombre: str | None = None,
        categoria_id: int | None = None,
        precio=None,
        stock_minimo=None,
    ) -> Producto:
        producto = self._uow.productos.obtener_por_id(producto_id)
        if producto is None:
            raise NotFoundError("El producto no existe")
        if not producto.pertenece_a(administrador_id):
            raise ProductoDeOtroAdministradorError(producto_id, administrador_id)

        if nombre is not None:
            producto.renombrar(NombreProducto(nombre))

        if categoria_id is not None:
            categoria = self._uow.categorias.obtener_por_id(categoria_id)
            if categoria is None:
                raise NotFoundError("La categoría no existe")
            producto.cambiar_categoria(categoria)

        if stock_minimo is not None:
            producto.cambiar_stock_minimo(StockMinimo(Decimal(str(stock_minimo))))

        self._uow.productos.guardar(producto)

        if precio is not None:
            self._fijar_precio_individual(administrador_id, producto, precio)

        return producto

    def eliminar(self, administrador_id: int, producto_id: int) -> None:
        producto = self._uow.productos.obtener_por_id(producto_id)
        if producto is None:
            raise NotFoundError("El producto no existe")
        if not producto.pertenece_a(administrador_id):
            raise ProductoDeOtroAdministradorError(producto_id, administrador_id)
        self._uow.productos.eliminar(producto_id)

    def _fijar_precio_individual(
        self, administrador_id: int, producto: Producto, precio
    ) -> None:
        if producto.id is None:
            raise NotFoundError("El producto no está persistido")
        administrador = self._uow.administradores.obtener_por_id(administrador_id)
        moneda = administrador.moneda.valor if administrador else "BOB"
        nuevo = _precio(precio, moneda)
        actual = self._uow.precios.obtener_vigente(
            producto.id, administrador_id, TipoCliente.INDIVIDUAL
        )
        if actual is not None:
            if actual.precio.amount == nuevo.amount:
                return
            actual.cerrar_vigencia()
            self._uow.precios.guardar(actual)

        self._uow.precios.guardar(
            PrecioProducto(
                administrador_id=administrador_id,
                producto_id=producto.id,
                tipo_cliente=TipoCliente.INDIVIDUAL,
                precio=nuevo,
            )
        )


class GestionarProveedor:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def crear(self, administrador_id: int, nombre: str, contacto: str | None = None):
        proveedor = Proveedor(
            administrador_id=administrador_id,
            nombre=nombre,
            contacto=contacto,
        )
        return self._uow.proveedores.guardar(proveedor)

    def actualizar(
        self,
        administrador_id: int,
        proveedor_id: int,
        nombre: str | None = None,
        contacto: str | None = None,
    ):
        proveedor = self._uow.proveedores.obtener_por_id(proveedor_id)
        if proveedor is None:
            raise NotFoundError("El proveedor no existe")
        proveedor.verificar_administrador(administrador_id)
        if nombre is not None:
            proveedor.nombre = texto_requerido(nombre, "proveedor", 150)
        if contacto is not None:
            proveedor.contacto = texto_opcional(contacto, "contacto", 150)
        return self._uow.proveedores.guardar(proveedor)

    def eliminar(self, administrador_id: int, proveedor_id: int) -> None:
        proveedor = self._uow.proveedores.obtener_por_id(proveedor_id)
        if proveedor is None:
            raise NotFoundError("El proveedor no existe")
        proveedor.verificar_administrador(administrador_id)
        self._uow.proveedores.eliminar(proveedor_id)
