# core/domain/usuario/value_objects.py
"""Value Objects del dominio Usuario"""

from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4
import re

from .exceptions import (
    UsuarioIdInvalidoException, 
    EmailInvalidoException,
    PasswordInvalidaException,
    NombreUsuarioInvalidoException,
    RolInvalidoException,
    PasswordHashInvalidoException
)


_EMAIL_REGEX = re.compile(
    r"^(?=.{1,254}$)"                       # longitud total máx.
    r"[A-Za-z0-9._%+-]+"                    # local-part
    r"@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"  # labels dominio
    r"[A-Za-z]{2,}$"                        # TLD
)


@dataclass(frozen=True)
class UsuarioId:
    """Value Object que identifica unívocamente a un Usuario (UUID v4)"""

    valor: UUID

    def __post_init__(self):
        if isinstance(self.valor, UUID):
            return

        # Caso 1: None
        if self.valor is None:
            raise UsuarioIdInvalidoException(
                usuario_id="<null>",
                code="USUARIO_ID_NULO",
                message_key="user.ID_NULL",
                message="User ID cannot be null",
            )

        # Caso 2: no es str ni UUID (int, list, dict, etc.)
        if not isinstance(self.valor, str):
            raise UsuarioIdInvalidoException(
                usuario_id=repr(self.valor),
                code="USUARIO_ID_TIPO_INVALIDO",
                message_key="user.ID_TYPE",
                message=f"User ID must be UUID or str, got {type(self.valor).__name__}",
            )

        # Caso 3: string vacío
        if not self.valor.strip():
            raise UsuarioIdInvalidoException(
                usuario_id="<empty>",
                code="USUARIO_ID_VACIO",
                message_key="user.ID_EMPTY",
                message="User ID cannot be empty",
            )

        # Caso 4: string con formato inválido
        try:
            object.__setattr__(self, "valor", UUID(self.valor))
        except ValueError:
            raise UsuarioIdInvalidoException(
                usuario_id=self.valor,
                code="USUARIO_ID_FORMATO_INVALIDO",
                message_key="user.ID_FORMAT",
                message="User ID has invalid format",
            )

    @classmethod
    def generar(cls) -> UsuarioId:
        return cls(uuid4())

    @classmethod
    def desde_str(cls, valor: str) -> UsuarioId:
        return cls(UUID(valor))

    def __str__(self) -> str:
        return str(self.valor)

    def __repr__(self) -> str:
        return f"UsuarioId({self.valor})"


@dataclass(frozen=True)
class Email:
    """Value Object que representa un email válido"""
    valor: str

    MAX_LENGTH = 254

    def __post_init__(self):
        self._validar()
        # Normalización: strip + lower
        object.__setattr__(self, "valor", self.valor.strip().lower())

    def _validar(self) -> None:
        # 1. Tipo
        if not isinstance(self.valor, str):
            raise EmailInvalidoException("NOT_STRING")

        # 2. Normalización previa para validar sobre el valor limpio
        valor = self.valor.strip().lower()

        # 3. Vacío
        if not valor:
            raise EmailInvalidoException("EMPTY")

        # 4. Longitud
        if len(valor) > self.MAX_LENGTH:
            raise EmailInvalidoException("TOO_LONG", max=self.MAX_LENGTH)

        # 5. Formato general
        if not _EMAIL_REGEX.match(valor):
            raise EmailInvalidoException("INVALID_FORMAT", email=self.valor)

        # 6. Local-part: sin puntos al inicio/fin ni consecutivos
        local = valor.split("@", 1)[0]
        if local.startswith(".") or local.endswith(".") or ".." in local:
            raise EmailInvalidoException("INVALID_LOCAL_PART", email=self.valor)



@dataclass(frozen=True)
class NombreUsuario:
    """Value Object que representa el nombre de un usuario"""
    valor: str

    MIN_LENGTH: int = 2
    MAX_LENGTH: int = 100

    def __post_init__(self):
        self._validar()

    def _validar(self) -> None:
        valor = self.valor

        if not valor or valor.strip() == "":
            raise NombreUsuarioInvalidoException("EMPTY")

        if len(valor.strip()) < self.MIN_LENGTH:
            raise NombreUsuarioInvalidoException("TOO_SHORT", min=self.MIN_LENGTH)

        if len(valor) > self.MAX_LENGTH:
            raise NombreUsuarioInvalidoException("TOO_LONG", max=self.MAX_LENGTH)


@dataclass(frozen=True)
class PasswordHash:
    """Value Object que envuelve un hash de contraseña (ya calculado en infraestructura)"""
    valor: str

    def __post_init__(self):
        if not self.valor or self.valor.strip() == "":
            raise PasswordHashInvalidoException("HASH_EMPTY")

@dataclass(frozen=True)
class RolUser:
    """Value Object que solo puede ser 'Vendedor' o 'Administrador'."""
    valor: str

    VENDEDOR = "vendedor"
    ADMINISTRADOR = "administrador"
    VALORES_VALIDOS = (VENDEDOR, ADMINISTRADOR)

    def __post_init__(self):
        self._validar()

    def _validar(self) -> None:
        if not isinstance(self.valor, str):
            raise RolInvalidoException("NOT_STRING")

        if self.valor.strip() == "":
            raise RolInvalidoException("EMPTY")

        if self.valor not in self.VALORES_VALIDOS:
            raise RolInvalidoException(
                "INVALID",
                valor=self.valor,
                valores_validos=", ".join(self.VALORES_VALIDOS),
            )

    @property
    def es_vendedor(self) -> bool:
        return self.valor == self.VENDEDOR

    @property
    def es_administrador(self) -> bool:
        return self.valor == self.ADMINISTRADOR

    def __str__(self) -> str:
        return self.valor
        


@dataclass(frozen=True)
class Password:
    """
    Value Object que representa una contraseña en texto plano.
    Valida reglas de complejidad en el momento de su creación.
    """
    valor: str

    LONGITUD_MINIMA = 8
    LONGITUD_MAXIMA = 128

    def __post_init__(self):
        self._validar()

    def _validar(self) -> None:
        if not isinstance(self.valor, str):
            raise PasswordInvalidaException("NOT_STRING")
        if self.valor.strip() == "":
            raise PasswordInvalidaException("EMPTY")
        if self.valor != self.valor.strip():
            raise PasswordInvalidaException("WHITESPACE_EDGES")
        if len(self.valor) < self.LONGITUD_MINIMA:
            raise PasswordInvalidaException("TOO_SHORT", min=self.LONGITUD_MINIMA)
        if len(self.valor) > self.LONGITUD_MAXIMA:
            raise PasswordInvalidaException("TOO_LONG", max=self.LONGITUD_MAXIMA)
        if not re.search(r"[A-Z]", self.valor):
            raise PasswordInvalidaException("NO_UPPERCASE")
        if not re.search(r"[a-z]", self.valor):
            raise PasswordInvalidaException("NO_LOWERCASE")
        if not re.search(r"\d", self.valor):
            raise PasswordInvalidaException("NO_DIGIT")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\[\]/\\;:'+=~`]", self.valor):
            raise PasswordInvalidaException("NO_SPECIAL")
        if re.search(r"\s", self.valor):
            raise PasswordInvalidaException("HAS_SPACES")
        if self._es_secuencial_o_repetitiva():
            raise PasswordInvalidaException("TOO_PREDICTABLE")

    def _es_secuencial_o_repetitiva(self) -> bool:
        # Detecta "aaaa", "1111", "abcd", "1234", etc.
        if re.search(r"(.)\1{3,}", self.valor):          # 4+ repetidos
            return True
        secuencias = ("0123456789", "abcdefghijklmnopqrstuvwxyz")
        bajo = self.valor.lower()
        for seq in secuencias:
            for i in range(len(seq) - 3):
                if seq[i:i+4] in bajo:
                    return True
        return False

    def __str__(self) -> str:
        return "********"      # nunca exponer el valor real

    def __repr__(self) -> str:
        return "Password(********)"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return NotImplemented
        return self.valor == other.valor

    def __hash__(self) -> int:
        return hash(self.valor)


@dataclass(frozen=True)
class EstadoUsuario:
    valor: str

    PENDIENTE = "pendiente"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    VALORES_VALIDOS = (PENDIENTE, ACTIVO, INACTIVO)

    def __post_init__(self):
        if self.valor not in self.VALORES_VALIDOS:
            raise EstadoUsuarioInvalidoException(self.valor)

    def puede_autenticarse(self) -> bool:
        return self.valor == self.ACTIVO

    def es_activo(self) -> bool:
        return self.valor == self.ACTIVO

    @classmethod
    def activo(cls) -> "EstadoUsuario":
        return cls(cls.ACTIVO)

    @classmethod
    def inactivo(cls) -> "EstadoUsuario":
        return cls(cls.INACTIVO)

    @classmethod
    def pendiente(cls) -> "EstadoUsuario":
        return cls(cls.PENDIENTE)
