 # apps/license/urls.py
from django.urls import path
from . import views

app_name = 'license'  # Namespace para evitar conflictos

urlpatterns = [
    path('', views.license_info, name="license_info"),

    # URL para activar licencia
    path('api/activar/', views.activar_licencia, name='activar'),
]
