# apps/usuarios/views/solicitud_admin.py
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.usuarios.models import AdministradorORM, SolicitudAdmin, VendedorORM
from apps.usuarios.serializers import SolicitudAdminSerializer


class SolicitudAdminListView(generics.ListAPIView):
    serializer_class = SolicitudAdminSerializer

    def get_queryset(self):
        queryset = SolicitudAdmin.objects.select_related(
            "vendedor__usuarioorm_ptr",
            "administrador__usuarioorm_ptr",
        )

        admin_id = self.request.query_params.get("admin_id")
        if admin_id:
            queryset = queryset.filter(administrador_id=admin_id)

        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class SolicitudAdminDetailView(generics.GenericAPIView):
    serializer_class = SolicitudAdminSerializer

    def post(self, request, pk):
        email = str(request.data.get("email_administrador") or "").strip().lower()
        mensaje = str(request.data.get("mensaje") or "").strip()

        if not email:
            return Response(
                {"error": "email_administrador es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vendedor = VendedorORM.objects.filter(pk=pk).first()
        if vendedor is None:
            return Response(
                {"error": "El vendedor no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        administrador = AdministradorORM.objects.filter(email=email).first()
        if administrador is None:
            return Response(
                {"error": "El administrador no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if SolicitudAdmin.objects.filter(
            vendedor=vendedor,
            administrador=administrador,
            estado=SolicitudAdmin.ESTADO_PENDIENTE,
        ).exists():
            return Response(
                {"error": "Ya existe una solicitud pendiente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            solicitud = SolicitudAdmin.objects.create(
                vendedor=vendedor,
                administrador=administrador,
                mensaje=mensaje[:200],
            )
        except IntegrityError:
            return Response(
                {"error": "Ya existe una solicitud pendiente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SolicitudAdminSerializer(solicitud).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, pk):
        return Response(SolicitudAdminSerializer(self._obtener(pk)).data)

    def patch(self, request, pk):
        solicitud = self._obtener(pk)

        if solicitud.estado != SolicitudAdmin.ESTADO_PENDIENTE:
            return Response(
                {"error": "La solicitud ya fue respondida"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nuevo_estado = request.data.get("estado")
        estados_validos = {
            SolicitudAdmin.ESTADO_ACEPTADA,
            SolicitudAdmin.ESTADO_RECHAZADA,
            SolicitudAdmin.ESTADO_BLOQUEADA,
        }
        if nuevo_estado not in estados_validos:
            return Response(
                {"error": "estado inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        solicitud.estado = nuevo_estado
        solicitud.respuesta_admin = str(
            request.data.get("respuesta_admin") or ""
        ).strip()[:200]
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save(
            update_fields=["estado", "respuesta_admin", "fecha_respuesta"],
        )

        if nuevo_estado == SolicitudAdmin.ESTADO_ACEPTADA:
            solicitud.vendedor.admins.add(solicitud.administrador)

        return Response(SolicitudAdminSerializer(solicitud).data)

    def delete(self, request, pk):
        self._obtener(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _obtener(self, pk):
        solicitud = (
            SolicitudAdmin.objects
            .select_related(
                "vendedor__usuarioorm_ptr",
                "administrador__usuarioorm_ptr",
            )
            .filter(pk=pk)
            .first()
        )
        if solicitud is None:
            raise NotFound("La solicitud no existe")
        return solicitud
