# apps/usuarios/views/registrar_admin.py
from core.application.usuario.crear_administrador import CrearAdministrador
from core.domain.shared.exceptions import DomainException
from infrastructure.django.auth.password_hasher_django import PasswordHasherDjango
from infrastructure.django.repositories.usuario_repository import DjangoUsuarioRepository
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegistrarAdministrador(APIView):
    use_case = CrearAdministrador(DjangoUsuarioRepository(), PasswordHasherDjango())
    
    permission_classes = []
    authentication_classes = []

    def post(self, request):        
        """
        Formato esperado del cuerpo (body):

        {
          "nombre": "Ana García",
          "email": "ana@example.com",
          "password_plana": "miPassword123",
        }
        """

        # Campos obligatorios que debe traer el JSON
        campos_requeridos = ["nombre", "email", "password_plana"]

        # Buscamos cuáles faltan (o vienen vacíos / None)
        faltantes = [
            campo for campo in campos_requeridos
            if not request.data.get(campo)
        ]

        if faltantes:
            return self._respuesta_error_validacion(campos_faltantes=faltantes) 


        try:
            admin_id = self.use_case.ejecutar(
                 request.data.get("nombre"), 
                 request.data.get("email"), 
                 request.data.get("password_plana"), 
            )
        except DomainException as e:
            return Response(e.to_dict(), status=e.status_code)
        
        return Response(
            {"mensaje": "OK", "id": str(admin_id)},
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
