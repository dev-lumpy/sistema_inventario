# core/domain/proveedor/exceptions.py
"""Excepciones del dominio Proveedor"""

from core.domain.shared.exceptions import DomainException


class ProveedorIdInvalidoException(DomainException):
    def __init__(self, id: str):
        super().__init__(
            code="PROVEEDOR_ID_INVALIDO",
            message=f"ID de proveedor inválido: {id}",
            status_code=400,
            field="ID de proveedor",
            id=id,
        )


class NombreProveedorInvalidoException(DomainException):
    def __init__(self, nombre: str, razon: str, min: int, max: int):
        super().__init__(
            code=razon,
            message=f"Nombre de proveedor inválido: {nombre}",
            status_code=400,
            field=nombre,
            min=min,
            max=max,
        )


class ProveedorNoEncontradoException(DomainException):
    def __init__(self, proveedor_id: str):
        super().__init__(
            code="PROVEEDOR_NO_ENCONTRADO",
            message=f"Proveedor no encontrado: {proveedor_id}",
            status_code=404,
            proveedor_id=proveedor_id,
        )