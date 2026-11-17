from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.accounts.exceptions import (
    TransicionVinculoInvalidaError,
    UsuarioInactivoError,
    VendedorBloqueadoError,
    VinculoNoAceptadoError,
)
from core.domain.accounts.value_objects import (
    Apellidos,
    Correo,
    Moneda,
    Nombre,
    NombreNegocio,
    PasswordHash,
    UserName,
)
from core.domain.shared.clock import now
from core.domain.shared.errors import ValidationError


@dataclass
class Usuario:
    nombre: Nombre
    user_name: UserName
    correo: Correo
    password_hash: PasswordHash
    apellidos: Apellidos = field(default_factory=Apellidos)
    debe_cambiar_password: bool = True
    activo: bool = True
    id: int | None = None
    creado_en: datetime = field(default_factory=now)

    def cambiar_password(self, nuevo_hash: PasswordHash, exigir_cambio: bool = True) -> None:
        self.password_hash = nuevo_hash
        self.debe_cambiar_password = exigir_cambio

    def marcar_password_cambiada(self) -> None:
        self.debe_cambiar_password = False

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def verificar_activo(self) -> None:
        if not self.activo:
            raise UsuarioInactivoError(self.id)

    def puede_autenticarse(self) -> bool:
        return self.activo


@dataclass
class Administrador:
    usuario: Usuario
    nombre_negocio: NombreNegocio = field(default_factory=NombreNegocio)
    moneda: Moneda = field(default_factory=Moneda)

    @property
    def id(self) -> int | None:
        return self.usuario.id

    @property
    def activo(self) -> bool:
        return self.usuario.activo


@dataclass
class Vendedor:
    usuario: Usuario
    creado_por_admin_id: int | None = None
    creado_en: datetime = field(default_factory=now)
    bloqueado: bool = False
    motivo_bloqueo: str | None = None
    bloqueado_en: datetime | None = None

    @property
    def id(self) -> int | None:
        return self.usuario.id

    def bloquear(self, motivo: str) -> None:
        if not motivo or not motivo.strip():
            raise ValidationError("El motivo de bloqueo es obligatorio")
        self.bloqueado = True
        self.motivo_bloqueo = motivo.strip()
        self.bloqueado_en = now()

    def desbloquear(self) -> None:
        self.bloqueado = False
        self.motivo_bloqueo = None
        self.bloqueado_en = None

    def verificar_puede_operar(self) -> None:
        self.usuario.verificar_activo()
        if self.bloqueado:
            raise VendedorBloqueadoError(self.id or 0)


@dataclass
class VinculoVendedorAdministrador:
    vendedor_id: int
    administrador_id: int
    solicitado_por: SolicitadoPor
    estado: EstadoVinculo = EstadoVinculo.PENDIENTE
    motivo_estado: str | None = None
    creado_en: datetime = field(default_factory=now)
    actualizado_en: datetime = field(default_factory=now)

    def aceptar(self) -> None:
        self._exigir_estado(EstadoVinculo.PENDIENTE, "aceptar")
        self.estado = EstadoVinculo.ACEPTADO
        self.motivo_estado = None
        self.actualizado_en = now()

    def rechazar(self, motivo: str) -> None:
        self._exigir_estado(EstadoVinculo.PENDIENTE, "rechazar")
        if not motivo or not motivo.strip():
            raise ValidationError("El motivo de rechazo es obligatorio")
        self.estado = EstadoVinculo.RECHAZADO
        self.motivo_estado = motivo.strip()
        self.actualizado_en = now()

    def inactivar(self, motivo: str) -> None:
        self._exigir_estado(EstadoVinculo.ACEPTADO, "inactivar")
        if not motivo or not motivo.strip():
            raise ValidationError("El motivo de inactivación es obligatorio")
        self.estado = EstadoVinculo.INACTIVO
        self.motivo_estado = motivo.strip()
        self.actualizado_en = now()

    def reactivar(self) -> None:
        self._exigir_estado(EstadoVinculo.INACTIVO, "reactivar")
        self.estado = EstadoVinculo.ACEPTADO
        self.motivo_estado = None
        self.actualizado_en = now()

    def puede_vender(self) -> bool:
        return self.estado == EstadoVinculo.ACEPTADO

    def verificar_puede_vender(self, vendedor_bloqueado: bool = False) -> None:
        if self.estado != EstadoVinculo.ACEPTADO:
            raise VinculoNoAceptadoError(
                self.vendedor_id, self.administrador_id, self.estado.value
            )
        if vendedor_bloqueado:
            raise VendedorBloqueadoError(self.vendedor_id)

    def _exigir_estado(self, esperado: EstadoVinculo, accion: str) -> None:
        if self.estado != esperado:
            raise TransicionVinculoInvalidaError(self.estado.value, accion)
