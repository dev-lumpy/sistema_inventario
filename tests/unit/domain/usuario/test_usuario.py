# pyright: reportAttributeAccessIssue=false
"""Pruebas unitarias para la entidad Usuario"""

import pytest
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import (
    UsuarioId,
    Email,
    NombreUsuario,
    PasswordHash,
)
from core.domain.usuario.rol import Rol
from core.domain.usuario.exceptions import (
    EmailInvalidoException,
    UsuarioInactivoException,
)


class TestUsuarioCreacion:
    def test_crear_usuario_admin(self):
        u = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("Admin"),
            email=Email("admin@example.com"),
            password_hash=PasswordHash("hash123"),
            rol=Rol.ADMINISTRADOR,
        )
        assert u.rol == Rol.ADMINISTRADOR
        assert u.puede_configurar() is True
        assert u.activo is True

    def test_crear_usuario_vendedor(self):
        u = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("Vendedor"),
            email=Email("vendedor@example.com"),
            password_hash=PasswordHash("hash456"),
            rol=Rol.VENDEDOR,
        )
        assert u.rol == Rol.VENDEDOR
        assert u.puede_configurar() is False

    def test_rol_por_defecto_vendedor(self):
        u = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("User"),
            email=Email("user@example.com"),
            password_hash=PasswordHash("hash789"),
        )
        assert u.rol == Rol.VENDEDOR

    def test_email_invalido_lanza_excepcion(self):
        with pytest.raises(EmailInvalidoException):
            Email("invalido")

    def test_email_sin_dominio_lanza_excepcion(self):
        with pytest.raises(EmailInvalidoException):
            Email("usuario@")

    def test_email_normaliza_a_minuscula(self):
        e = Email("User@Example.COM")
        assert e.valor == "user@example.com"


class TestUsuarioMetodos:
    def _crear_admin(self):
        return Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("Admin"),
            email=Email("admin@test.com"),
            password_hash=PasswordHash("hash"),
            rol=Rol.ADMINISTRADOR,
        )

    def _crear_vendedor(self):
        return Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("Vendedor"),
            email=Email("ven@test.com"),
            password_hash=PasswordHash("hash"),
            rol=Rol.VENDEDOR,
        )

    def test_cambiar_rol(self):
        u = self._crear_admin()
        u.cambiar_rol(Rol.VENDEDOR)
        assert u.puede_configurar() is False

    def test_cambiar_password(self):
        u = self._crear_admin()
        u.cambiar_password(PasswordHash("nuevo_hash"))
        assert u.password_hash.valor == "nuevo_hash"

    def test_desactivar(self):
        u = self._crear_admin()
        u.desactivar()
        assert u.activo is False

    def test_activar(self):
        u = self._crear_admin()
        u.desactivar()
        u.activar()
        assert u.activo is True

    def test_verificar_activo_pasa(self):
        u = self._crear_admin()
        u.verificar_activo()

    def test_verificar_inactivo_lanza_excepcion(self):
        u = self._crear_admin()
        u.desactivar()
        with pytest.raises(UsuarioInactivoException):
            u.verificar_activo()


class TestUsuarioIdentidad:
    def test_igualdad_por_id(self):
        id = UsuarioId.generar()
        u1 = Usuario(
            id=id,
            nombre=NombreUsuario("User A"),
            email=Email("a@test.com"),
            password_hash=PasswordHash("h1"),
        )
        u2 = Usuario(
            id=id,
            nombre=NombreUsuario("User B"),
            email=Email("b@test.com"),
            password_hash=PasswordHash("h2"),
        )
        assert u1 == u2
        assert hash(u1) == hash(u2)

    def test_distintos_id_son_distintos(self):
        u1 = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("User A"),
            email=Email("a@test.com"),
            password_hash=PasswordHash("h1"),
        )
        u2 = Usuario(
            id=UsuarioId.generar(),
            nombre=NombreUsuario("User A"),
            email=Email("a@test.com"),
            password_hash=PasswordHash("h1"),
        )
        assert u1 != u2