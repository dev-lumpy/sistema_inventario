from __future__ import annotations

import re
from dataclasses import dataclass

from core.application.ports.accounts import UsuarioRepository
from core.application.ports.password_hasher import PasswordHasher
from core.application.ports.unit_of_work import UnitOfWork
from core.domain.accounts.entities import (
    Administrador,
    Usuario,
    Vendedor,
    VinculoVendedorAdministrador,
)
from core.domain.accounts.enums import EstadoVinculo, SolicitadoPor
from core.domain.accounts.exceptions import UsuarioInactivoError
from core.domain.accounts.value_objects import Correo, Nombre, UserName
from core.domain.shared.errors import (
    AuthenticationFailedError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


@dataclass
class ResultadoAutenticacion:
    usuario: Usuario
    rol: str


def _base_user_name(preferido: str) -> str:
    base = re.sub(r"[^A-Za-z0-9_.-]", "", preferido.strip().lower())
    if not base:
        base = "usuario"
    if len(base) < 3:
        base = f"user{base}"
    return base[:40]


def generar_user_name(preferido: str, repo: UsuarioRepository) -> UserName:
    base = _base_user_name(preferido)
    candidato = base
    intento = 1
    while repo.obtener_por_user_name(candidato) is not None:
        intento += 1
        candidato = f"{base}{intento}"[:50]
    return UserName(candidato)


class RegistrarAdministrador:
    def __init__(self, uow: UnitOfWork, password_hasher: PasswordHasher) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    def ejecutar(self, nombre: str, email: str, password: str) -> Administrador:
        correo = Correo(email)
        if self._uow.usuarios.obtener_por_correo(correo.valor) is not None:
            raise ConflictError("El correo ya está registrado", correo=correo.valor)
        if not password or len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")

        user_name = generar_user_name(correo.valor.split("@")[0], self._uow.usuarios)
        usuario = Usuario(
            nombre=Nombre(nombre),
            user_name=user_name,
            correo=correo,
            password_hash=self._password_hasher.hashear(password),
            debe_cambiar_password=False,
        )
        self._uow.usuarios.guardar(usuario)
        administrador = Administrador(usuario=usuario)
        self._uow.administradores.guardar(administrador)
        return administrador


class RegistrarVendedor:
    def __init__(self, uow: UnitOfWork, password_hasher: PasswordHasher) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    def ejecutar(
        self,
        nombre: str,
        email: str,
        password: str,
        admin_username: str | None = None,
    ) -> Vendedor:
        correo = Correo(email)
        if self._uow.usuarios.obtener_por_correo(correo.valor) is not None:
            raise ConflictError("El correo ya está registrado", correo=correo.valor)
        if not password or len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")

        administrador = None
        if admin_username:
            admin_usuario = self._uow.usuarios.obtener_por_user_name(admin_username)
            if admin_usuario is None:
                admin_usuario = self._uow.usuarios.obtener_por_nombre(admin_username)
            if admin_usuario is None or admin_usuario.id is None:
                raise NotFoundError("El administrador no existe")
            administrador = self._uow.administradores.obtener_por_id(admin_usuario.id)
            if administrador is None:
                raise ValidationError("El usuario indicado no es administrador")

        user_name = generar_user_name(correo.valor.split("@")[0], self._uow.usuarios)
        usuario = Usuario(
            nombre=Nombre(nombre),
            user_name=user_name,
            correo=correo,
            password_hash=self._password_hasher.hashear(password),
            debe_cambiar_password=True,
        )
        self._uow.usuarios.guardar(usuario)
        vendedor = Vendedor(
            usuario=usuario,
            creado_por_admin_id=administrador.id if administrador else None,
        )
        self._uow.vendedores.guardar(vendedor)

        if administrador is not None and administrador.id is not None:
            self._uow.vinculos.guardar(
                VinculoVendedorAdministrador(
                    vendedor_id=usuario.id or 0,
                    administrador_id=administrador.id,
                    estado=EstadoVinculo.ACEPTADO,
                    solicitado_por=SolicitadoPor.ADMIN,
                )
            )
        return vendedor


class AutenticarUsuario:
    def __init__(self, uow: UnitOfWork, password_hasher: PasswordHasher) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    def ejecutar(self, identificador: str, password: str) -> ResultadoAutenticacion:
        usuario = self._uow.usuarios.obtener_por_correo(identificador)
        if usuario is None:
            usuario = self._uow.usuarios.obtener_por_user_name(identificador)
        if usuario is None or usuario.id is None:
            raise AuthenticationFailedError("Credenciales inválidas")

        try:
            usuario.verificar_activo()
        except UsuarioInactivoError as exc:
            raise AuthenticationFailedError("La cuenta está inactiva") from exc

        if not self._password_hasher.verificar(password, usuario.password_hash):
            raise AuthenticationFailedError("Credenciales inválidas")

        administrador = self._uow.administradores.obtener_por_id(usuario.id)
        vendedor = self._uow.vendedores.obtener_por_id(usuario.id)
        if administrador is not None:
            rol = "administrador"
        elif vendedor is not None:
            rol = "vendedor"
        else:
            raise AuthenticationFailedError("El usuario no tiene un rol asignado")

        return ResultadoAutenticacion(usuario=usuario, rol=rol)
