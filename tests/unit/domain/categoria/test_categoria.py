# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para la entidad Categoria"""

import pytest
from core.domain.categoria.categoria import Categoria
from core.domain.categoria.value_objects import CategoriaId, NombreCategoria
from core.domain.categoria.exceptions import (
    NombreCategoriaInvalidoException,
    CategoriaNoEncontradaException,
)
from core.domain.shared.fecha import Fecha


class TestCategoriaCreacion:
    def test_crear_categoria_valida(self):
        id = CategoriaId.generar()
        nombre = NombreCategoria("Electrónicos")
        cat = Categoria(id=id, nombre=nombre)
        assert cat.id == id
        assert cat.nombre.valor == "Electrónicos"
        assert cat.activa is True
        assert cat.fecha_creacion is not None

    def test_crear_categoria_inactiva(self):
        cat = Categoria(
            id=CategoriaId.generar(),
            nombre=NombreCategoria("Ropa"),
            activa=False,
        )
        assert cat.activa is False

    def test_crear_categoria_nombre_vacio_lanza_excepcion(self):
        with pytest.raises(NombreCategoriaInvalidoException):
            NombreCategoria("")

    def test_crear_categoria_nombre_muy_corto_lanza_excepcion(self):
        with pytest.raises(NombreCategoriaInvalidoException):
            NombreCategoria("A")

    def test_crear_categoria_nombre_muy_largo_lanza_excepcion(self):
        with pytest.raises(NombreCategoriaInvalidoException):
            NombreCategoria("A" * 51)


class TestCategoriaMetodos:
    def _crear(self, nombre="Electrónicos"):
        return Categoria(
            id=CategoriaId.generar(),
            nombre=NombreCategoria(nombre),
        )

    def test_renombrar(self):
        cat = self._crear()
        cat.renombrar(NombreCategoria("Tecnología"))
        assert cat.nombre.valor == "Tecnología"

    def test_activar(self):
        cat = self._crear()
        cat.desactivar()
        assert cat.activa is False
        cat.activar()
        assert cat.activa is True

    def test_desactivar(self):
        cat = self._crear()
        cat.desactivar()
        assert cat.activa is False


class TestCategoriaIdentidad:
    def test_igualdad_por_id(self):
        id = CategoriaId.generar()
        c1 = Categoria(id=id, nombre=NombreCategoria("Cat A"))
        c2 = Categoria(id=id, nombre=NombreCategoria("Cat B"))
        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_distintos_id_son_distintos(self):
        c1 = Categoria(id=CategoriaId.generar(), nombre=NombreCategoria("Cat A"))
        c2 = Categoria(id=CategoriaId.generar(), nombre=NombreCategoria("Cat A"))
        assert c1 != c2