# apps/usuarios/urls.py

from django.urls import re_path

from .views import (
    RegistrarAdministrador,
    RegistrarVendedor,
    AutenticarUsuario,
    CerrarSesion,
    RefrescarToken
)


urlpatterns = [
    re_path(r'^registrar-admin/?$', RegistrarAdministrador.as_view()),
    re_path(r'^registrar-vendedor/?$', RegistrarVendedor.as_view()),

    # Públicas (authentication_classes = [])
    re_path(r'^auth/login/?$', AutenticarUsuario.as_view(), name='login'),
    re_path(r'^auth/refresh/?$', RefrescarToken.as_view(), name='refresh'),
    re_path(r'^auth/logout/?$', CerrarSesion.as_view(), name='logout'),
    re_path(r'^auth/registro/?$', RegistrarAdministrador.as_view(), name='registro'),
]
