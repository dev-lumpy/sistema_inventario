# apps/usuarios/urls.py

from django.urls import path
from .views import RegistrarAdministrador, RegistrarVendedor


urlpatterns = [
    path("registrar-admin/", RegistrarAdministrador.as_view()),
    path("registrar-vendedor/", RegistrarVendedor.as_view()),
]
