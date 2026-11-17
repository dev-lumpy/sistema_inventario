from django.urls import path

from .views import dashboard_page, index, login_page, logout_page, register_page

app_name = "pages"

urlpatterns = [
    path("", index, name="inicio"),
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("logout/", logout_page, name="logout"),
]
