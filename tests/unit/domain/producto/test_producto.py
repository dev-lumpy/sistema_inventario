# pyright: reportAttributeAccessIssue=false
# tests/unit/domain/producto/test_producto.py

"""Pruebas unitarias para la entidad Producto (Aggregate Root)"""

import pytest
from uuid import UUID
from core.domain.producto.producto import Producto
from core.domain.producto.estado_stock import EstadoStock
from core.domain.producto.value_objects import (
    ProductoId,
    NombreProducto,
    Precio,
    Cantidad,
    StockMinimo,
)
from core.domain.producto.exceptions import (
    ProductoInactivoException,
    StockPorDebajoDelMinimoException,
    StockInsuficienteException,
    NombreProductoInvalidoException,
    PrecioInvalidoException,
    CantidadInvalidaException,
    StockMinimoInvalidoException,
)
from core.domain.shared.fecha import Fecha


class TestProductoCreacion:
    """Pruebas para la creación de productos"""

    def _crear_producto_valido(self, **kwargs):
        defaults = {
            "id": ProductoId.generar(),
            "nombre": NombreProducto("Producto Test"),
            "precio": Precio(100.00),
            "cantidad_inicial": Cantidad(50),
            "stock_minimo": StockMinimo(10),
            "categoria_id": "Electrónicos",
            "activo": True,
        }
        defaults.update(kwargs)
        return Producto(**defaults)

    # ============ TESTS DE CREACIÓN EXITOSA ============

    def test_crear_producto_valido(self):
        """Debe crear un producto correctamente con todos los atributos"""
        id = ProductoId.generar()
        nombre = NombreProducto("Laptop HP")
        precio = Precio(1500.00)
        cantidad = Cantidad(100)
        stock_minimo = StockMinimo(20)

        producto = Producto(
            id=id,
            nombre=nombre,
            precio=precio,
            cantidad_inicial=cantidad,
            stock_minimo=stock_minimo,
            categoria_id="Electrónicos",
            activo=True,
        )

        assert producto.id == id
        assert producto.nombre == nombre
        assert producto.nombre.valor == "Laptop HP"
        assert producto.precio == precio
        assert producto.precio.valor == 1500.00
        assert producto.cantidad == cantidad
        assert producto.cantidad.valor == 100
        assert producto.stock_minimo == stock_minimo
        assert producto.stock_minimo.valor == 20
        assert producto.categoria_id == "Electrónicos"
        assert producto.activo is True
        assert producto.fecha_creacion is not None

    def test_crear_producto_con_stock_mayor_al_minimo(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10),
        )
        assert producto.cantidad.valor == 50
        assert producto.cantidad.valor > producto.stock_minimo.valor

    def test_crear_producto_con_stock_igual_al_minimo(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(10),
            stock_minimo=StockMinimo(10),
        )
        assert producto.cantidad.valor == 10
        assert producto.cantidad.valor == producto.stock_minimo.valor

    def test_crear_producto_activo_por_defecto(self):
        producto = Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Producto Test"),
            precio=Precio(100.00),
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10),
        )
        assert producto.activo is True

    def test_crear_producto_con_stock_cero(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(0),
            stock_minimo=StockMinimo(0),
        )
        assert producto.cantidad.valor == 0
        assert producto.esta_en_alerta() is True

    def test_crear_producto_con_stock_minimo_cero(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(5),
            stock_minimo=StockMinimo(0),
        )
        assert producto.stock_minimo.valor == 0
        assert producto.esta_en_alerta() is False

    # ============ TESTS DE VALIDACIÓN ============

    def test_crear_producto_con_stock_menor_al_minimo_lanza_excepcion(self):
        with pytest.raises(StockPorDebajoDelMinimoException) as exc_info:
            Producto(
                id=ProductoId.generar(),
                nombre=NombreProducto("Producto Test"),
                precio=Precio(100.00),
                cantidad_inicial=Cantidad(5),
                stock_minimo=StockMinimo(10),
            )
        assert exc_info.value.stock_actual == 5
        assert exc_info.value.stock_minimo == 10

    # ============ TESTS DE REPRESENTACIÓN ============

    def test_repr_del_producto_creado(self):
        producto = self._crear_producto_valido()
        repr_str = repr(producto)
        assert "Producto" in repr_str
        assert "Producto Test" in repr_str
        assert "100.0" in repr_str

    def test_producto_recien_creado_no_esta_en_alerta_si_stock_suficiente(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10),
        )
        assert producto.esta_en_alerta() is False

    def test_producto_recien_creado_esta_en_alerta_si_stock_insuficiente(self):
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(15),
            stock_minimo=StockMinimo(10),
        )
        producto.reducir_stock(10)
        assert producto.esta_en_alerta() is True


class TestEstadoStock:
    """Pruebas para la derivación de EstadoStock"""

    def test_disponible_cuando_stock_supera_minimo(self):
        p = self._crear_producto()
        assert p.estado_stock() == EstadoStock.DISPONIBLE
        assert p.esta_disponible() is True
        assert p.esta_bajo_stock() is False
        assert p.esta_agotado() is False
        assert p.esta_en_alerta() is False

    def test_bajo_cuando_stock_igual_al_minimo(self):
        p = self._crear_producto(cantidad=10, minimo=10)
        assert p.estado_stock() == EstadoStock.BAJO
        assert p.esta_bajo_stock() is True
        assert p.esta_en_alerta() is True

    def test_bajo_cuando_stock_menor_al_minimo(self):
        """Crear con stock valido, luego reducir por debajo del minimo"""
        p = self._crear_producto(cantidad=10, minimo=10)
        p.reducir_stock(5)  # ahora 5 < 10
        assert p.estado_stock() == EstadoStock.BAJO

    def test_agotado_cuando_stock_cero(self):
        p = self._crear_producto(cantidad=5, minimo=5)
        p.reducir_stock(5)
        assert p.estado_stock() == EstadoStock.AGOTADO
        assert p.esta_agotado() is True
        assert p.esta_en_alerta() is True

    def test_agotado_despues_de_reducir_stock(self):
        p = self._crear_producto(cantidad=5, minimo=5)
        p.reducir_stock(5)
        assert p.estado_stock() == EstadoStock.AGOTADO

    def test_vuelve_a_disponible_despues_de_aumentar_stock(self):
        p = self._crear_producto(cantidad=10, minimo=5)
        p.reducir_stock(10)  # queda en 0, AGOTADO
        assert p.estado_stock() == EstadoStock.AGOTADO
        p.aumentar_stock(10)  # vuelve a 10, DISPONIBLE
        assert p.estado_stock() == EstadoStock.DISPONIBLE

    def _crear_producto(self, cantidad=50, minimo=10):
        return Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Artículo X"),
            precio=Precio(100.00),
            cantidad_inicial=Cantidad(cantidad),
            stock_minimo=StockMinimo(minimo),
        )


class TestProductoIdentidad:
    """Pruebas para identidad (__eq__, __hash__)"""

    def test_dos_productos_con_mismo_id_son_iguales(self):
        id = ProductoId.generar()
        p1 = Producto(id=id, nombre=NombreProducto("Artículo A"), precio=Precio(10), cantidad_inicial=Cantidad(5), stock_minimo=StockMinimo(1))
        p2 = Producto(id=id, nombre=NombreProducto("Artículo B"), precio=Precio(20), cantidad_inicial=Cantidad(5), stock_minimo=StockMinimo(1))
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_dos_productos_con_distinto_id_son_distintos(self):
        p1 = Producto(id=ProductoId.generar(), nombre=NombreProducto("Artículo A"), precio=Precio(10), cantidad_inicial=Cantidad(5), stock_minimo=StockMinimo(1))
        p2 = Producto(id=ProductoId.generar(), nombre=NombreProducto("Artículo A"), precio=Precio(10), cantidad_inicial=Cantidad(5), stock_minimo=StockMinimo(1))
        assert p1 != p2

    def test_igualdad_con_no_producto_retorna_not_implemented(self):
        p = Producto(id=ProductoId.generar(), nombre=NombreProducto("Artículo A"), precio=Precio(10), cantidad_inicial=Cantidad(5), stock_minimo=StockMinimo(1))
        assert (p == 1) is False


class TestProductoMetodos:
    """Pruebas para los métodos de dominio"""

    def _crear_producto_valido(self, activo=True):
        return Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Producto Test"),
            precio=Precio(100.00),
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10),
            activo=activo,
        )

    def test_actualizar_precio_producto_activo(self):
        p = self._crear_producto_valido()
        p.actualizar_precio(Precio(200.00))
        assert p.precio.valor == 200.00

    def test_actualizar_precio_producto_inactivo_lanza_excepcion(self):
        p = self._crear_producto_valido(activo=False)
        with pytest.raises(ProductoInactivoException):
            p.actualizar_precio(Precio(200.00))

    def test_aumentar_stock_producto_activo(self):
        p = self._crear_producto_valido()
        p.aumentar_stock(10)
        assert p.cantidad.valor == 60

    def test_aumentar_stock_producto_inactivo_lanza_excepcion(self):
        p = self._crear_producto_valido(activo=False)
        with pytest.raises(ProductoInactivoException):
            p.aumentar_stock(10)

    def test_reducir_stock_producto_activo(self):
        p = self._crear_producto_valido()
        p.reducir_stock(10)
        assert p.cantidad.valor == 40

    def test_reducir_stock_producto_inactivo_lanza_excepcion(self):
        p = self._crear_producto_valido(activo=False)
        with pytest.raises(ProductoInactivoException):
            p.reducir_stock(10)

    def test_reducir_stock_insuficiente_lanza_excepcion(self):
        p = self._crear_producto_valido()
        with pytest.raises(StockInsuficienteException):
            p.reducir_stock(100)

    def test_activar_producto(self):
        p = self._crear_producto_valido(activo=False)
        assert p.activo is False
        p.activar()
        assert p.activo is True

    def test_desactivar_producto(self):
        p = self._crear_producto_valido()
        p.desactivar()
        assert p.activo is False

    def test_aumentar_stock_con_cero_lanza_value_error(self):
        p = self._crear_producto_valido()
        with pytest.raises(ValueError):
            p.aumentar_stock(0)

    def test_reducir_stock_con_cero_lanza_value_error(self):
        p = self._crear_producto_valido()
        with pytest.raises(ValueError):
            p.reducir_stock(0)


class TestProductoFechaCreacion:
    """Pruebas para fecha_creacion"""

    def test_fecha_creacion_asignada_automaticamente(self):
        p = Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Artículo Z"),
            precio=Precio(100),
            cantidad_inicial=Cantidad(10),
            stock_minimo=StockMinimo(1),
        )
        assert p.fecha_creacion is not None

    def test_fecha_creacion_personalizada(self):
        fecha = Fecha.desde_iso("2024-01-01T00:00:00+00:00")
        p = Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Artículo Y"),
            precio=Precio(100),
            cantidad_inicial=Cantidad(10),
            stock_minimo=StockMinimo(1),
            fecha_creacion=fecha,
        )
        assert p.fecha_creacion == fecha

    def test_fecha_creacion_en_utc(self):
        p = Producto(
            id=ProductoId.generar(),
            nombre=NombreProducto("Artículo W"),
            precio=Precio(100),
            cantidad_inicial=Cantidad(10),
            stock_minimo=StockMinimo(1),
        )
        assert p.fecha_creacion.valor.tzinfo is not None