# core/domain/categoria/exceptions.py
"""Excepciones del dominio Categoria"""

from core.domain.shared.exceptions import DomainException


class CategoriaIdInvalidoException(DomainException):
    """Se lanza cuando el ID de categoría no es válido"""

    def __init__(self, id: str):
        super().__init__(
            code="CATEGORIA_ID_INVALIDO",
            message=f"ID de categoría inválido: {id}",
            status_code=400,
            field="ID de categoría",
            id=id,
        )


class NombreCategoriaInvalidoException(DomainException):
    """Se lanza cuando el nombre no cumple las reglas"""

    def __init__(self, nombre: str, razon: str, min: int, max: int):
        super().__init__(
            code=razon,
            message=f"Nombre de categoría inválido: {nombre}",
            status_code=400,
            field=nombre,
            min=min,
            max=max,
        )


class CategoriaNoEncontradaException(DomainException):
    """Se lanza cuando no se encuentra una categoría por ID"""

    def __init__(self, categoria_id: str):
        super().__init__(
            code="CATEGORIA_NO_ENCONTRADA",
            message=f"Categoría no encontrada: {categoria_id}",
            status_code=404,
            categoria_id=categoria_id,
        )


class CategoriaDuplicadaException(DomainException):
    """Se lanza cuando se intenta crear una categoría con nombre duplicado"""

    def __init__(self, nombre: str):
        super().__init__(
            code="CATEGORIA_DUPLICADA",
            message=f"Categoría duplicada: {nombre}",
            status_code=409,
            field=nombre,
        )