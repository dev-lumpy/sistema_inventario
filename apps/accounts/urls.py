from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RefreshView,
    RegistrarAdministradorView,
    RegistrarVendedorView,
    SolicitudAdminDetailView,
    SolicitudAdminListView,
    VendedorDetalleView,
    VendedoresPorAdminView,
)

urlpatterns = [
    path("registrar-admin/", RegistrarAdministradorView.as_view(), name="registrar-admin"),
    path("registrar-vendedor/", RegistrarVendedorView.as_view(), name="registrar-vendedor"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/registro/", RegistrarAdministradorView.as_view(), name="registro"),
    path(
        "get_user/admin/<int:admin_id>/vendedores/",
        VendedoresPorAdminView.as_view(),
        name="vendedores-por-admin",
    ),
    path("api/<int:usuario_id>/", VendedorDetalleView.as_view(), name="usuario-detalle"),
    path("solicitudes-admin/", SolicitudAdminListView.as_view(), name="solicitudes-admin-list"),
    path(
        "solicitudes-admin/<str:pk>/",
        SolicitudAdminDetailView.as_view(),
        name="solicitudes-admin-detail",
    ),
]
