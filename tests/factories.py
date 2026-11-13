"""Factories compartidas para los tests del proyecto."""

import decimal

import factory
from django.contrib.auth.hashers import make_password

from apps.inventario.models import (
    Categoria,
    MovimientoStock,
    Producto,
    Proveedor,
)
from apps.usuarios.models import AdministradorORM


class AdministradorFactory(factory.django.DjangoModelFactory):
    """Administrador mínimo válido para autenticar requests de prueba.

    Supuesto: AdministradorORM hereda de AbstractBaseUser, por lo que
    ``is_authenticated`` es True. Si el modelo cambia, ajustar esta factory.
    """

    class Meta:
        model = AdministradorORM

    username = factory.Sequence(lambda n: f"admin_test_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.LazyFunction(lambda: make_password("Clave#2026"))
    activo = "activo"


class CategoriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Categoria

    nombre = factory.Sequence(lambda n: f"Categoría {n}")


class ProveedorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proveedor

    nombre = factory.Sequence(lambda n: f"Proveedor {n}")
    contacto = "Contacto de prueba"
    telefono = "381-555-0000"
    email = factory.Sequence(lambda n: f"proveedor{n}@test.com")
    activo = True


class ProductoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Producto

    nombre = factory.Sequence(lambda n: f"Producto {n}")
    categoria = factory.SubFactory(CategoriaFactory)
    precio_unitario = decimal.Decimal("100.00")
    stock_minimo = 1
    administrador = factory.SubFactory(AdministradorFactory)
    activo = True


class MovimientoStockFactory(factory.django.DjangoModelFactory):
    """Movimiento válido por defecto (entrada por stock inicial).

    Para ventas usar tipo='S', motivo='venta' y canal_venta.
    Para compras usar motivo='compra' y proveedor.
    """

    class Meta:
        model = MovimientoStock

    producto = factory.SubFactory(ProductoFactory)
    tipo = MovimientoStock.TIPO_ENTRADA
    motivo = MovimientoStock.MOTIVO_INICIAL
    cantidad = 10
    detalle = ""
    canal_venta = None
    proveedor = None
