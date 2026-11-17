from __future__ import annotations

from core.application.ports.unit_of_work import UnitOfWork
from core.domain.accounts.entities import Administrador, Usuario, Vendedor
from core.domain.accounts.value_objects import Correo, Moneda, NombreNegocio, UserName
from core.domain.shared.errors import ConflictError, NotFoundError, ValidationError


class ListarVendedores:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(self, administrador_id: int) -> list[Vendedor]:
        return self._uow.vendedores.listar_por_administrador(administrador_id)


class ActualizarUsuario:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        usuario_id: int,
        user_name: str | None = None,
        correo: str | None = None,
        activo: bool | None = None,
    ) -> Usuario:
        usuario = self._uow.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise NotFoundError("El usuario no existe")

        if user_name is not None:
            nuevo_user_name = UserName(user_name)
            existente = self._uow.usuarios.obtener_por_user_name(nuevo_user_name.valor)
            if existente is not None and existente.id != usuario.id:
                raise ConflictError("El nombre de usuario ya está en uso")
            usuario.user_name = nuevo_user_name

        if correo is not None:
            nuevo_correo = Correo(correo)
            existente = self._uow.usuarios.obtener_por_correo(nuevo_correo.valor)
            if existente is not None and existente.id != usuario.id:
                raise ConflictError("El correo ya está registrado")
            usuario.correo = nuevo_correo

        if activo is not None:
            if activo:
                usuario.activar()
            else:
                usuario.desactivar()

        if usuario.id is None:
            raise ValidationError("El usuario no está persistido")
        self._uow.usuarios.guardar(usuario)
        return usuario


class EliminarUsuario:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(self, usuario_id: int) -> None:
        if self._uow.usuarios.obtener_por_id(usuario_id) is None:
            raise NotFoundError("El usuario no existe")
        self._uow.usuarios.eliminar(usuario_id)


class ObtenerPerfilAdministrador:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(self, administrador_id: int) -> Administrador:
        administrador = self._uow.administradores.obtener_por_id(administrador_id)
        if administrador is None:
            raise NotFoundError("El administrador no existe")
        return administrador


class ActualizarPerfilAdministrador:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def ejecutar(
        self,
        administrador_id: int,
        nombre_negocio: str | None = None,
        moneda: str | None = None,
    ) -> Administrador:
        administrador = self._uow.administradores.obtener_por_id(administrador_id)
        if administrador is None:
            raise NotFoundError("El administrador no existe")

        if nombre_negocio is not None:
            administrador.nombre_negocio = NombreNegocio(nombre_negocio)
        if moneda is not None:
            administrador.moneda = Moneda(moneda)

        self._uow.administradores.guardar(administrador)
        return administrador
