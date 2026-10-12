from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.application.ports import password_hasher
from core.application.usuario.crear_vendedor import CrearVendedor
from core.domain.shared.exceptions import DomainException
from core.domain.usuario.exceptions import UsuarioIdInvalidoException
from core.domain.usuario.usuario import Usuario
from core.domain.usuario.value_objects import UsuarioId, NombreUsuario
from infrastructure.django.auth.password_hasher_django import PasswordHasherDjango
from infrastructure.django.repositories.usuario_repository import DjangoUsuarioRepository

class RegistrarVendedor(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK) 

    def post(self, request):
        """
        Formato esperado del cuerpo (body):

        {
          "nombre": "Ana García",
          "email": "ana@example.com",
          "password": "miPassword123",
          "username": "el_user_name_del_admin"
        }
        """

        # Campos obligatorios que debe traer el JSON
        campos_requeridos = ["nombre", "email", "password", "username"]

        # Buscamos cuáles faltan (o vienen vacíos / None)
        faltantes = [
            campo for campo in campos_requeridos
            if not request.data.get(campo)
        ]

        if faltantes:
            return self._respuesta_error_validacion(campos_faltantes=faltantes)

        
        # Extraemos los valores (ya sabemos que todos existen)
        nombre         = request.data.get("nombre")
        email          = request.data.get("email")
        password       = request.data.get("password")
        username       = request.data.get("username")

        # Primero verificamos si admin_id es un UUID valido
        try:
            username = NombreUsuario(username)
        except UsuarioIdInvalidoException as e:
            return self._respuesta_error_validacion(
                mensaje="Datos inválidos",
                error_campo={
                    "admin_id": e.user_message,   # ya viene localizado desde el catálogo
                    "codigo": e.code,             # ej: "USUARIO_ID_FORMATO_INVALIDO"
                },
            )

        usuario = CrearVendedor(
            DjangoUsuarioRepository(),
            PasswordHasherDjango()
        )

        admin_id = usuario.usuario_repo.obtener_id_for_username(username)
        if admin_id == None:
            return self._respuesta_error_validacion(
                mensaje="El usuario administrador no existe",
                error_campo={"username": "No existe un administrador con ese username"},
            )

        try:
            id_usuario = usuario.ejecutar(
                nombre,
                email,
                password,
                admin_id
            )
        except DomainException as e:
            return Response(e.to_dict(), status=e.status_code)

        return Response(
            {"mensaje": "OK"},
            status=status.HTTP_201_CREATED,
        )


    def _respuesta_error_validacion(
        self,
        *,
        campos_faltantes: list[str] | None = None,
        error_campo: dict | None = None,
        mensaje: str = "Faltan campos obligatorios",
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        """
        Construye una respuesta de error de validación incluyendo
        solo los bloques que se pasen (no None).
        """
        body: dict = {"error": mensaje}

        if campos_faltantes is not None:
            body["campos_faltantes"] = campos_faltantes

        if error_campo is not None:
            body["error_campo"] = error_campo

        return Response(body, status=http_status)
