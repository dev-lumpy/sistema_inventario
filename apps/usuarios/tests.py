from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from apps.inventario.views.producto import ProductoInsertAPIView
from apps.usuarios.models import AdministradorORM, VendedorORM
from apps.usuarios.permissions import (
    IsAdministrador,
    IsAdministradorOrReadOnly,
    IsVendedorOrAdministrador,
)


class RolePermissionTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def request_for(self, role, method="get"):
        request = getattr(self.factory, method)("/")
        request.user = SimpleNamespace(is_authenticated=True, rol=role)
        return request

    def test_seller_can_read_inventory_but_cannot_manage_it(self):
        read_permission = IsAdministradorOrReadOnly()
        self.assertTrue(read_permission.has_permission(self.request_for("vendedor"), None))
        self.assertFalse(
            read_permission.has_permission(
                self.request_for("vendedor", "post"),
                None,
            )
        )

    def test_admin_only_permission_rejects_seller(self):
        self.assertFalse(
            IsAdministrador().has_permission(self.request_for("vendedor"), None)
        )
        self.assertTrue(
            IsAdministrador().has_permission(self.request_for("administrador"), None)
        )

    def test_seller_and_admin_can_register_sales(self):
        permission = IsVendedorOrAdministrador()
        for role in ("vendedor", "administrador"):
            with self.subTest(role=role):
                self.assertTrue(
                    permission.has_permission(self.request_for(role, "post"), None)
                )

    def test_seller_is_denied_product_creation_endpoint(self):
        request = self.factory.post("/api/inventario/productos/", {}, format="json")
        force_authenticate(
            request,
            user=SimpleNamespace(is_authenticated=True, rol="vendedor"),
        )

        response = ProductoInsertAPIView.as_view()(request)

        self.assertEqual(response.status_code, 403)


class RegistrationPersistenceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_admin_registration_is_saved(self):
        response = self.client.post(
            "/api/usuarios/registrar-admin/",
            {
                "nombre": "admin_registro_test",
                "email": "admin_registro_test@gmail.com",
                "password": "Clave#2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        admin = AdministradorORM.objects.get(email="admin_registro_test@gmail.com")
        self.assertTrue(admin.check_password("Clave#2026"))

        login_response = self.client.post(
            "/api/usuarios/auth/login/",
            {
                "email": "admin_registro_test@gmail.com",
                "password": "Clave#2026",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, 200, login_response.data)

    def test_seller_registration_is_saved(self):
        response = self.client.post(
            "/api/usuarios/registrar-vendedor/",
            {
                "nombre": "vendedor_registro_test",
                "email": "vendedor_registro_test@gmail.com",
                "password": "Clave#2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        seller = VendedorORM.objects.get(email="vendedor_registro_test@gmail.com")
        self.assertTrue(seller.check_password("Clave#2026"))

        login_response = self.client.post(
            "/api/usuarios/auth/login/",
            {
                "email": "vendedor_registro_test@gmail.com",
                "password": "Clave#2026",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, 200, login_response.data)

        username_login_response = self.client.post(
            "/api/usuarios/auth/login/",
            {
                "email": "VENDEDOR_REGISTRO_TEST",
                "password": "Clave#2026",
            },
            format="json",
        )
        self.assertEqual(
            username_login_response.status_code,
            200,
            username_login_response.data,
        )
