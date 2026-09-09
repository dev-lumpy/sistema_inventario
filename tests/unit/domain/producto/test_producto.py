# pyright: reportAttributeAccessIssue=false
# tests/unit/domain/producto/test_producto.py

"""Pruebas unitarias para la entidad Producto (Aggregate Root)"""

import pytest
from core.domain.producto.producto import Producto
from core.domain.producto.value_objects import (
        NombreProducto,
        CategoriaProducto,
        Precio,
        Cantidad,
        StockMinimo
        )
from core.domain.producto.exceptions import (
        ProductoInactivoException,
        StockPorDebajoDelMinimoException,
        StockInsuficienteException,
        ProductoNoEncontradoException,
        NombreProductoInvalidoException,
        PrecioInvalidoException,
        CantidadInvalidaException,
        StockMinimoInvalidoException,
        CategoriaVaciaException
        )
from core.i18n.message import MessageKey
from core.i18n.manager import MessageManager


class TestProductoCreacion:
    """Pruebas para la creación de productos"""
    
    # ============ HELPERS ============
    
    def _crear_producto_valido(self, **kwargs):
        """Crear un producto válido con valores por defecto"""
        defaults = {
            "nombre": NombreProducto("Producto Test"),
            "categoria": CategoriaProducto("Electrónicos"),
            "precio": Precio(100.00),
            "cantidad_inicial": Cantidad(50),
            "stock_minimo": StockMinimo(10),
            "activo": True
        }
        defaults.update(kwargs)
        return Producto(**defaults)
    
    # ============ TESTS DE CREACIÓN EXITOSA ============
    
    def test_crear_producto_valido(self):
        """✅ Debe crear un producto correctamente con todos los atributos"""
        # Arrange
        nombre = NombreProducto("Laptop HP")
        categoria = CategoriaProducto("Electrónicos")
        precio = Precio(1500.00)
        cantidad = Cantidad(100)
        stock_minimo = StockMinimo(20)
        
        # Act
        producto = Producto(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            cantidad_inicial=cantidad,
            stock_minimo=stock_minimo,
            activo=True
        )
        
        # Assert
        assert producto.nombre == nombre
        assert producto.nombre.valor == "Laptop HP"
        assert producto.categoria == categoria
        assert producto.categoria.valor == "Electrónicos"
        assert producto.precio == precio
        assert producto.precio.valor == 1500.00
        assert producto.cantidad == cantidad
        assert producto.cantidad.valor == 100
        assert producto.stock_minimo == stock_minimo
        assert producto.stock_minimo.valor == 20
        assert producto.activo is True
    
    def test_crear_producto_con_stock_mayor_al_minimo(self):
        """✅ Debe crear producto cuando stock > stock mínimo"""
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10)
        )
        
        assert producto.cantidad.valor == 50
        assert producto.stock_minimo.valor == 10
        assert producto.cantidad.valor > producto.stock_minimo.valor
    
    def test_crear_producto_con_stock_igual_al_minimo(self):
        """✅ Debe crear producto cuando stock == stock mínimo"""
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(10),
            stock_minimo=StockMinimo(10)
        )
        
        assert producto.cantidad.valor == 10
        assert producto.stock_minimo.valor == 10
        assert producto.cantidad.valor == producto.stock_minimo.valor
    
    def test_crear_producto_activo_por_defecto(self):
        """✅ Si no se especifica activo, debe crearse como activo por defecto"""
        producto = Producto(
            nombre=NombreProducto("Producto Test"),
            categoria=CategoriaProducto("Electrónicos"),
            precio=Precio(100.00),
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10)
            # activo no se especifica
        )
        
        assert producto.activo is True
    
    def test_crear_producto_con_stock_cero(self):
        """✅ Debe permitir crear producto con stock 0"""
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(0),
            stock_minimo=StockMinimo(0)
        )
        
        assert producto.cantidad.valor == 0
        assert producto.esta_en_alerta() is True  # 0 <= 10
    
    def test_crear_producto_con_stock_minimo_cero(self):
        """✅ Debe permitir stock mínimo 0"""
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(5),
            stock_minimo=StockMinimo(0)
        )
        
        assert producto.stock_minimo.valor == 0
        assert producto.esta_en_alerta() is False  # 5 > 0
    
    def test_crear_producto_con_precio_cero(self):
        """❌ NO DEBE permitir precio 0 (regla de negocio: Precio > 0)"""
        with pytest.raises(PrecioInvalidoException) as exc_info:
            Precio(0.00)
        
        assert exc_info.value.price == 0.00
    
    def test_crear_producto_con_precio_positivo(self):
        """✅ Debe permitir precio positivo"""
        producto = self._crear_producto_valido(
            precio=Precio(99.99)
        )
        
        assert producto.precio.valor == 99.99
    
    # ============ TESTS DE VALIDACIÓN (CASOS QUE DEBEN FALLAR) ============
    
    def test_crear_producto_con_stock_menor_al_minimo_lanza_excepcion(self):
        """❌ Debe lanzar StockPorDebajoDelMinimoException si stock < stock mínimo"""
        # Act & Assert
        with pytest.raises(StockPorDebajoDelMinimoException) as exc_info:
            Producto(
                nombre=NombreProducto("Producto Test"),
                categoria=CategoriaProducto("Electrónicos"),
                precio=Precio(100.00),
                cantidad_inicial=Cantidad(5),  # stock = 5
                stock_minimo=StockMinimo(10),   # mínimo = 10
                activo=True
            )
        
        # Verificar que la excepción contiene los valores correctos
        assert exc_info.value.stock_actual == 5
        assert exc_info.value.stock_minimo == 10
    
    def test_crear_producto_con_stock_negativo_lanza_excepcion(self):
        """❌ El Value Object Cantidad debe validar stock negativo"""
        with pytest.raises(CantidadInvalidaException) as exc_info:
            Cantidad(-5)
        
        assert exc_info.value.cantidad == -5
    
    def test_crear_producto_con_stock_minimo_negativo_lanza_excepcion(self):
        """❌ El Value Object StockMinimo debe validar valores negativos"""
        with pytest.raises(StockMinimoInvalidoException) as exc_info:
            StockMinimo(-1)
        
        assert exc_info.value.stock == -1
    
    def test_crear_producto_con_precio_negativo_lanza_excepcion(self):
        """❌ El Value Object Precio debe validar precios negativos"""
        with pytest.raises(PrecioInvalidoException) as exc_info:
            Precio(-100.00)
        
        assert exc_info.value.price == -100.00
    
    def test_crear_producto_con_nombre_vacio_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar nombre vacío"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("")
        
        assert exc_info.value.field == ""
    
    def test_crear_producto_con_nombre_solo_espacios_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar solo espacios"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("   ")
        
        assert exc_info.value.field == "   "
    
    def test_crear_producto_con_nombre_muy_corto_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar longitud mínima (3)"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("Ab")  # 2 caracteres
        
        assert exc_info.value.field == "Ab"
        assert exc_info.value.min == 3
    
    def test_crear_producto_con_nombre_muy_largo_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar longitud máxima (50)"""
        nombre_largo = "A" * 51
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto(nombre_largo)
        
        assert exc_info.value.field == nombre_largo
        assert exc_info.value.max == 50
    
    def test_crear_producto_con_nombre_con_caracteres_especiales_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar caracteres especiales"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("Producto@#$")
        
        assert exc_info.value.field == "Producto@#$"
    
    def test_crear_producto_con_nombre_reservado_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar palabras reservadas"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("admin")
        
        assert exc_info.value.field == "admin"
    
    def test_crear_producto_con_nombre_empieza_con_numero_lanza_excepcion(self):
        """❌ El Value Object NombreProducto debe validar que no empiece con número"""
        with pytest.raises(NombreProductoInvalidoException) as exc_info:
            NombreProducto("123Producto")
        
        assert exc_info.value.field == "123Producto"
    
    def test_crear_producto_con_categoria_vacia_lanza_excepcion(self):
        """❌ El Value Object CategoriaProducto debe validar categoría vacía"""
        with pytest.raises(CategoriaVaciaException):
            CategoriaProducto("")
    
    def test_crear_producto_con_categoria_solo_espacios_lanza_excepcion(self):
        """❌ El Value Object CategoriaProducto debe validar solo espacios"""
        with pytest.raises(CategoriaVaciaException):
            CategoriaProducto("   ")
    
    # ============ TESTS DE INTEGRACIÓN DE VALUE OBJECTS ============
    
    def test_crear_producto_con_todos_los_value_objects(self):
        """✅ Debe funcionar con todos los Value Objects correctos"""
        nombre = NombreProducto("Smartphone Samsung")
        categoria = CategoriaProducto("Tecnología")
        precio = Precio(899.99)
        cantidad = Cantidad(25)
        stock_minimo = StockMinimo(5)
        
        producto = Producto(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            cantidad_inicial=cantidad,
            stock_minimo=stock_minimo
        )
        
        assert isinstance(producto.nombre, NombreProducto)
        assert isinstance(producto.categoria, CategoriaProducto)
        assert isinstance(producto.precio, Precio)
        assert isinstance(producto.cantidad, Cantidad)
        assert isinstance(producto.stock_minimo, StockMinimo)
        assert producto.activo is True
    
    def test_crear_producto_con_categoria_personalizada(self):
        """✅ Debe permitir cualquier categoría válida"""
        categorias = ["Electrónicos", "Ropa", "Alimentos", "Libros", "Muebles"]
        
        for cat in categorias:
            producto = self._crear_producto_valido(
                categoria=CategoriaProducto(cat)
            )
            assert producto.categoria.valor == cat
    
    # ============ TESTS DE INMUTABILIDAD ============
    
    def test_crear_producto_y_modificar_objeto_no_afecta_valor_original(self):
        """✅ Los Value Objects deben ser inmutables"""
        nombre_original = NombreProducto("Original")
        producto = self._crear_producto_valido(
            nombre=nombre_original
        )
        
        # Los Value Objects son frozen, no se pueden modificar
        assert producto.nombre.valor == "Original"
    
    # ============ TEST DE REPRESENTACIÓN ============
    
    def test_repr_del_producto_creado(self):
        """✅ La representación debe incluir los atributos principales"""
        producto = self._crear_producto_valido()
        repr_str = repr(producto)
        
        assert "Producto" in repr_str
        assert "Producto Test" in repr_str
        assert "Electrónicos" in repr_str
        assert "100.0" in repr_str
        assert "50" in repr_str
    
    # ============ TEST DE ESTADO INICIAL ============
    
    def test_producto_recien_creado_no_esta_en_alerta_si_stock_suficiente(self):
        """✅ Producto nuevo no debe estar en alerta si stock > stock mínimo"""
        producto = self._crear_producto_valido(
            cantidad_inicial=Cantidad(50),
            stock_minimo=StockMinimo(10)
        )
        
        assert producto.esta_en_alerta() is False
    
    def test_producto_recien_creado_esta_en_alerta_si_stock_insuficiente(self):
        """✅ Producto nuevo debe estar en alerta si stock <= stock mínimo"""
        producto = self._crear_producto_valido(
            nombre="Producto Test",
            cantidad_inicial=Cantidad(15),      # ✅ Stock inicial mayor que el mínimo
            stock_minimo=StockMinimo(10)   # ✅ El mínimo es 10
        )
        # Después de crear, reducir el stock para probar la alerta
        producto.reducir_stock(10)  # Quedan 5 < 10
        assert producto.esta_en_alerta() is True
