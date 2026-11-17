from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/usuarios/", include("apps.accounts.urls")),
    path("api/inventario/", include("apps.catalog.urls")),
    path("", include("apps.pages.urls")),
]
