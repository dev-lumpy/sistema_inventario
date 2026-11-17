from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.accounts.entities import (
    Administrador,
    Usuario,
    Vendedor,
    VinculoVendedorAdministrador,
)
from core.domain.accounts.enums import EstadoVinculo


class UsuarioRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        ...

    @abstractmethod
    def obtener_por_user_name(self, user_name: str) -> Usuario | None:
        ...

    @abstractmethod
    def obtener_por_correo(self, correo: str) -> Usuario | None:
        ...

    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        ...

    @abstractmethod
    def listar(self) -> list[Usuario]:
        ...

    @abstractmethod
    def eliminar(self, usuario_id: int) -> None:
        ...


class AdministradorRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, administrador_id: int) -> Administrador | None:
        ...

    @abstractmethod
    def guardar(self, administrador: Administrador) -> Administrador:
        ...

    @abstractmethod
    def listar(self) -> list[Administrador]:
        ...


class VendedorRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, vendedor_id: int) -> Vendedor | None:
        ...

    @abstractmethod
    def guardar(self, vendedor: Vendedor) -> Vendedor:
        ...

    @abstractmethod
    def listar_por_administrador(self, administrador_id: int) -> list[Vendedor]:
        ...


class VinculoRepository(ABC):
    @abstractmethod
    def obtener(
        self, vendedor_id: int, administrador_id: int
    ) -> VinculoVendedorAdministrador | None:
        ...

    @abstractmethod
    def guardar(
        self, vinculo: VinculoVendedorAdministrador
    ) -> VinculoVendedorAdministrador:
        ...

    @abstractmethod
    def listar_por_administrador(
        self, administrador_id: int, estado: EstadoVinculo | None = None
    ) -> list[VinculoVendedorAdministrador]:
        ...

    @abstractmethod
    def listar_por_vendedor(
        self, vendedor_id: int
    ) -> list[VinculoVendedorAdministrador]:
        ...
