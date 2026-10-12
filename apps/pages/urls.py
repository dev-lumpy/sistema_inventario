from django.urls import re_path
from .views import dashboard_page, login_page, register_page, index

app_name = "pages"

urlpatterns = [
    re_path(r'^$', index, name="inicio"),
    re_path(r'^login/?$', login_page, name="login"),
    re_path(r'^dashboard/?$', dashboard_page, name="dashboard"),
    re_path(r'^register/?$', register_page, name="register"),
]
