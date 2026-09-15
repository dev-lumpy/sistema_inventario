# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para la entidad Proveedor"""

import pytest
from core.domain.proveedor.proveedor import Proveedor
from core.domain.proveedor.value_objects import (
    ProveedorId,
    NombreProveedor,
    ContactoProveedor,
)
from core.domain.proveedor.exceptions import NombreProveedorInvalidoException


class TestProveedorCreacion:
    def test_crear_proveedor_valido(self):
        id = ProveedorId.generar()
        p = Proveedor(
            id=id,
            nombre=NombreProveedor("Distribuidora ABC"),
            contacto=ContactoProveedor("555-0100"),
        )
        assert p.id == id
        assert p.nombre.valor == "Distribuidora ABC"
        assert p.contacto.valor == "555-0100"
        assert p.activo is True
        assert p.fecha_creacion is not None

    def test_crear_proveedor_sin_contacto(self):
        p = Proveedor(
            id=ProveedorId.generar(),
            nombre=NombreProveedor("Mayorista XYZ"),
        )
        assert p.contacto.valor == ""

    def test_nombre_vacio_lanza_excepcion(self):
        with pytest.raises(NombreProveedorInvalidoException):
            NombreProveedor("")

    def test_nombre_muy_corto_lanza_excepcion(self):
        with pytest.raises(NombreProveedorInvalidoException):
            NombreProveedor("AB")


class TestProveedorMetodos:
    def _crear(self):
        return Proveedor(
            id=ProveedorId.generar(),
            nombre=NombreProveedor("Distribuidora ABC"),
        )

    def test_actualizar_contacto(self):
        p = self._crear()
        p.actualizar_contacto(ContactoProveedor("nuevo@email.com"))
        assert p.contacto.valor == "nuevo@email.com"

    def test_desactivar(self):
        p = self._crear()
        p.desactivar()
        assert p.activo is False

    def test_activar(self):
        p = self._crear()
        p.desactivar()
        p.activar()
        assert p.activo is True


class TestProveedorIdentidad:
    def test_igualdad_por_id(self):
        id = ProveedorId.generar()
        p1 = Proveedor(id=id, nombre=NombreProveedor("Prov A"))
        p2 = Proveedor(id=id, nombre=NombreProveedor("Prov B"))
        assert p1 == p2

    def test_distintos_id_son_distintos(self):
        p1 = Proveedor(id=ProveedorId.generar(), nombre=NombreProveedor("Prov A"))
        p2 = Proveedor(id=ProveedorId.generar(), nombre=NombreProveedor("Prov A"))
        assert p1 != p2