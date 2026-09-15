# pyright: reportAttributeAccessIssue=false
"""Pruebas para el caso de uso CrearCategoria"""

from core.application.categoria.crear_categoria import (
    CrearCategoria,
    CrearCategoriaInput,
)
from core.adapters import CategoriaRepositoryMemoria


class TestCrearCategoria:
    def test_crear_categoria_exitoso(self):
        repo = CategoriaRepositoryMemoria()
        use_case = CrearCategoria(repo)

        output = use_case.ejecutar(CrearCategoriaInput(nombre="Electrónicos"))
        assert output.categoria_id is not None
        assert len(repo.listar_todas()) == 1

        categoria = repo.listar_todas()[0]
        assert categoria.nombre.valor == "Electrónicos"