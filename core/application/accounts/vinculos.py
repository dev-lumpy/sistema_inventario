from __future__ import annotations

from core.application.ports.unit_of_work import UnitOfWork
from core.domain.accounts.entities import VinculoVendedorAdministrador
from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.shared.errors import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


class SolicitarVinculo:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self, vendedor_id: int, email_administrador: str, motivo: str | None = None
    ) -> VinculoVendedorAdministrador:
        if self._uow.vendedores.obtener_por_id(vendedor_id) is None:
            raise NotFoundError("El vendedor no existe")
        admin_usuario = self._uow.usuarios.obtener_por_correo(email_administrador)
        if admin_usuario is None or admin_usuario.id is None:
            raise NotFoundError("El administrador no existe")
        administrador = self._uow.administradores.obtener_por_id(admin_usuario.id)
        if administrador is None:
            raise ValidationError("El usuario indicado no es administrador")

        existente = self._uow.vinculos.obtener(vendedor_id, admin_usuario.id)
        if existente is not None and existente.estado in (
            EstadoVinculo.PENDIENTE,
            EstadoVinculo.ACEPTADO,
        ):
            raise ConflictError("Ya existe una solicitud pendiente o aceptada")

        vinculo = VinculoVendedorAdministrador(
            vendedor_id=vendedor_id,
            administrador_id=admin_usuario.id,
            solicitado_por=SolicitadoPor.VENDEDOR,
            motivo_estado=motivo,
        )
        self._uow.vinculos.guardar(vinculo)
        return vinculo


class ResponderVinculo:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        vendedor_id: int,
        administrador_id: int,
        nuevo_estado: str,
        motivo: str | None = None,
    ) -> VinculoVendedorAdministrador:
        vinculo = self._uow.vinculos.obtener(vendedor_id, administrador_id)
        if vinculo is None:
            raise NotFoundError("El vínculo no existe")

        if nuevo_estado == EstadoVinculo.ACEPTADO.value:
            vinculo.aceptar()
        elif nuevo_estado == EstadoVinculo.RECHAZADO.value:
            vinculo.rechazar(motivo or "")
        elif nuevo_estado == EstadoVinculo.INACTIVO.value:
            vinculo.inactivar(motivo or "")
        else:
            raise ValidationError("Estado de vínculo inválido", estado=nuevo_estado)

        self._uow.vinculos.guardar(vinculo)
        return vinculo


class CancelarVinculo:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(self, vendedor_id: int, administrador_id: int) -> None:
        vinculo = self._uow.vinculos.obtener(vendedor_id, administrador_id)
        if vinculo is None:
            raise NotFoundError("El vínculo no existe")
        if vinculo.estado == EstadoVinculo.ACEPTADO:
            raise ConflictError("No se puede cancelar un vínculo aceptado")
        self._uow.vinculos.eliminar(vendedor_id, administrador_id)


class ListarSolicitudes:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self, administrador_id: int, estado: EstadoVinculo | None = None
    ) -> list[VinculoVendedorAdministrador]:
        return self._uow.vinculos.listar_por_administrador(administrador_id, estado)
