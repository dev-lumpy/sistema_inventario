from __future__ import annotations

from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.application.accounts.gestion import (
    ActualizarUsuario,
    EliminarUsuario,
    ListarVendedores,
)
from core.application.accounts.registro import (
    AutenticarUsuario,
    RegistrarAdministrador,
    RegistrarVendedor,
)
from core.application.accounts.vinculos import (
    CancelarVinculo,
    ListarSolicitudes,
    ResponderVinculo,
    SolicitarVinculo,
)
from core.domain.accounts.enums import EstadoVinculo
from core.domain.shared.errors import DomainError, NotFoundError, PermissionDeniedError

from infrastructure.django.unit_of_work import DjangoUnitOfWork

from apps.accounts.authentication import UsuarioSesion
from apps.accounts.password_hasher import DjangoPasswordHasher
from apps.accounts.permissions import EsAdministrador, EsAdministradorOVendedor
from apps.common.exceptions import responder_domain_error


def _uow() -> DjangoUnitOfWork:
    return DjangoUnitOfWork()


def _hasher() -> DjangoPasswordHasher:
    return DjangoPasswordHasher()


def _error_registro(exc: DomainError) -> Response:
    return Response(
        {
            "error": {
                "message": exc.message,
                "code": exc.code,
                "details": exc.context,
            }
        },
        status=getattr(exc, "status_code", None) or 400,
    )


def _serializar_vendedor(vendedor) -> dict:
    return {
        "uuid": str(vendedor.id),
        "username": vendedor.usuario.user_name.valor,
        "email": vendedor.usuario.correo.valor,
        "activo": "activo" if vendedor.usuario.activo else "inactivo",
        "bloqueado": vendedor.bloqueado,
        "fecha_creacion": vendedor.creado_en.isoformat(),
    }


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        identificador = str(
            request.data.get("email")
            or request.data.get("correo")
            or request.data.get("username")
            or ""
        ).strip()
        password = str(request.data.get("password") or "")

        if not identificador or not password:
            return Response(
                {"detail": "Correo o usuario y contraseña son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with _uow() as uow:
                resultado = AutenticarUsuario(uow, _hasher()).ejecutar(
                    identificador, password
                )
        except DomainError as exc:
            return responder_domain_error(exc)

        request.session.cycle_key()
        request.session["usuario_id"] = resultado.usuario.id
        request.session["rol"] = resultado.rol
        request.session["nombre"] = resultado.usuario.nombre.valor

        return Response(
            {
                "status": "ok",
                "rol": resultado.rol,
                "nombre": resultado.usuario.nombre.valor,
            }
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        request.session.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        return Response({"status": "ok"})


class RegistrarAdministradorView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        nombre = str(request.data.get("nombre") or "").strip()
        email = str(request.data.get("email") or "").strip()
        password = str(request.data.get("password") or "")

        if not nombre or not email or not password:
            return Response(
                {"error": {"message": "Faltan campos obligatorios"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with _uow() as uow:
                administrador = RegistrarAdministrador(uow, _hasher()).ejecutar(
                    nombre, email, password
                )
        except DomainError as exc:
            return _error_registro(exc)

        return Response(
            {
                "mensaje": "OK",
                "id": administrador.id,
                "username": administrador.usuario.user_name.valor,
            },
            status=status.HTTP_201_CREATED,
        )


class RegistrarVendedorView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "OK"})

    def post(self, request):
        nombre = str(request.data.get("nombre") or "").strip()
        email = str(request.data.get("email") or "").strip()
        password = str(request.data.get("password") or "")
        admin_username = request.data.get("username")
        admins = request.data.get("admins")
        if not admin_username and isinstance(admins, list) and admins:
            admin_username = admins[0]

        if not nombre or not email or not password:
            return Response(
                {"error": {"message": "Faltan campos obligatorios"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with _uow() as uow:
                vendedor = RegistrarVendedor(uow, _hasher()).ejecutar(
                    nombre,
                    email,
                    password,
                    str(admin_username).strip() if admin_username else None,
                )
        except DomainError as exc:
            return _error_registro(exc)

        return Response(
            {
                "mensaje": "OK",
                "id": vendedor.id,
                "username": vendedor.usuario.user_name.valor,
            },
            status=status.HTTP_201_CREATED,
        )


class VendedoresPorAdminView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request, admin_id: int):
        if request.user.id != admin_id:
            raise PermissionDeniedError("No podés consultar vendedores de otro administrador")
        with _uow() as uow:
            vendedores = ListarVendedores(uow).ejecutar(admin_id)
        return Response([_serializar_vendedor(vendedor) for vendedor in vendedores])


class VendedorDetalleView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request, usuario_id: int):
        with _uow() as uow:
            vendedor = self._obtener(uow, usuario_id, request.user.id)
            return Response(_serializar_vendedor(vendedor))

    def patch(self, request, usuario_id: int):
        activo = request.data.get("activo")
        activo_bool = None
        if activo is not None:
            activo_bool = str(activo).lower() == "activo"

        try:
            with _uow() as uow:
                self._obtener(uow, usuario_id, request.user.id)
                usuario = ActualizarUsuario(uow).ejecutar(
                    usuario_id,
                    user_name=request.data.get("username"),
                    correo=request.data.get("email"),
                    activo=activo_bool,
                )
                vendedor = uow.vendedores.obtener_por_id(usuario_id)
                if vendedor is None:
                    raise NotFoundError("El vendedor no existe")
                vendedor.usuario = usuario
                return Response(_serializar_vendedor(vendedor))
        except DomainError as exc:
            return responder_domain_error(exc)
        except IntegrityError:
            return Response(
                {"detail": "El nombre de usuario o correo ya está en uso."},
                status=status.HTTP_409_CONFLICT,
            )

    def delete(self, request, usuario_id: int):
        try:
            with _uow() as uow:
                self._obtener(uow, usuario_id, request.user.id)
                EliminarUsuario(uow).ejecutar(usuario_id)
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ProtectedError):
            return Response(
                {"detail": "No se puede eliminar el vendedor porque tiene ventas registradas."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _obtener(uow: DjangoUnitOfWork, usuario_id: int, administrador_id: int):
        vendedor = uow.vendedores.obtener_por_id(usuario_id)
        if vendedor is None:
            raise NotFoundError("El vendedor no existe")
        vinculo = uow.vinculos.obtener(usuario_id, administrador_id)
        if vinculo is None or vinculo.estado != EstadoVinculo.ACEPTADO:
            raise NotFoundError("El vendedor no pertenece a este administrador")
        return vendedor


class SolicitudAdminListView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def get(self, request):
        estado_valor = request.query_params.get("estado")
        estado = None
        if estado_valor:
            try:
                estado = EstadoVinculo(estado_valor)
            except ValueError:
                return Response(
                    {"detail": "Estado de solicitud inválido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with _uow() as uow:
            if isinstance(request.user, UsuarioSesion) and request.user.rol == "administrador":
                vinculos = ListarSolicitudes(uow).ejecutar(request.user.id, estado)
            else:
                vinculos = [
                    vinculo
                    for vinculo in uow.vinculos.listar_por_vendedor(request.user.id)
                    if estado is None or vinculo.estado == estado
                ]
            return Response([self._serializar(uow, vinculo) for vinculo in vinculos])

    def post(self, request):
        if request.user.rol != "vendedor":
            raise PermissionDeniedError("Solo un vendedor puede solicitar un administrador")
        email = str(request.data.get("email_administrador") or "").strip()
        mensaje = str(request.data.get("mensaje") or "").strip() or None
        if not email:
            return Response(
                {"detail": "El email del administrador es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with _uow() as uow:
                vinculo = SolicitarVinculo(uow).ejecutar(
                    request.user.id, email, mensaje
                )
                return Response(
                    self._serializar(uow, vinculo),
                    status=status.HTTP_201_CREATED,
                )
        except DomainError as exc:
            return responder_domain_error(exc)

    @staticmethod
    def _serializar(uow: DjangoUnitOfWork, vinculo) -> dict:
        vendedor = uow.vendedores.obtener_por_id(vinculo.vendedor_id)
        administrador = uow.administradores.obtener_por_id(vinculo.administrador_id)
        return {
            "id": f"{vinculo.vendedor_id}:{vinculo.administrador_id}",
            "vendedor": {
                "uuid": str(vinculo.vendedor_id),
                "username": vendedor.usuario.user_name.valor if vendedor else "—",
                "email": vendedor.usuario.correo.valor if vendedor else "—",
            },
            "administrador": {
                "uuid": str(vinculo.administrador_id),
                "username": (
                    administrador.usuario.user_name.valor if administrador else "—"
                ),
                "email": (
                    administrador.usuario.correo.valor if administrador else "—"
                ),
            },
            "mensaje": vinculo.motivo_estado or "",
            "estado": vinculo.estado.value,
            "fecha_creacion": vinculo.creado_en.isoformat(),
        }


class SolicitudAdminDetailView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def get(self, request, pk: str):
        vendedor_id, administrador_id = self._parse(pk)
        with _uow() as uow:
            vinculo = self._obtener(uow, vendedor_id, administrador_id, request.user)
            return Response(SolicitudAdminListView._serializar(uow, vinculo))

    def patch(self, request, pk: str):
        if request.user.rol != "administrador":
            raise PermissionDeniedError("Solo un administrador puede responder")
        vendedor_id, administrador_id = self._parse(pk)
        if administrador_id != request.user.id:
            raise PermissionDeniedError("La solicitud no pertenece a este administrador")
        estado = str(request.data.get("estado") or "").strip()
        estado = {
            "aceptada": EstadoVinculo.ACEPTADO.value,
            "rechazada": EstadoVinculo.RECHAZADO.value,
            "bloqueada": EstadoVinculo.INACTIVO.value,
        }.get(estado, estado)
        motivo = str(
            request.data.get("respuesta_admin") or request.data.get("motivo") or ""
        ).strip()
        try:
            with _uow() as uow:
                vinculo = ResponderVinculo(uow).ejecutar(
                    vendedor_id, administrador_id, estado, motivo or None
                )
                return Response(SolicitudAdminListView._serializar(uow, vinculo))
        except DomainError as exc:
            return responder_domain_error(exc)

    def delete(self, request, pk: str):
        if request.user.rol != "vendedor":
            raise PermissionDeniedError("Solo el vendedor puede cancelar su solicitud")
        vendedor_id, administrador_id = self._parse(pk)
        if vendedor_id != request.user.id:
            raise PermissionDeniedError("La solicitud no pertenece a este vendedor")
        try:
            with _uow() as uow:
                self._obtener(uow, vendedor_id, administrador_id, request.user)
                CancelarVinculo(uow).ejecutar(vendedor_id, administrador_id)
        except DomainError as exc:
            return responder_domain_error(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _parse(pk: str) -> tuple[int, int]:
        try:
            vendedor_id, administrador_id = pk.split(":")
            return int(vendedor_id), int(administrador_id)
        except (ValueError, AttributeError) as exc:
            from core.domain.shared.errors import ValidationError

            raise ValidationError("Identificador de solicitud inválido") from exc

    @staticmethod
    def _obtener(uow: DjangoUnitOfWork, vendedor_id: int, administrador_id: int, user):
        vinculo = uow.vinculos.obtener(vendedor_id, administrador_id)
        if vinculo is None:
            raise NotFoundError("La solicitud no existe")
        if user.rol == "administrador" and administrador_id != user.id:
            raise NotFoundError("La solicitud no existe")
        if user.rol == "vendedor" and vendedor_id != user.id:
            raise NotFoundError("La solicitud no existe")
        return vinculo
