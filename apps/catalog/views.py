from __future__ import annotations

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.application.catalog.gestion import (
    GestionarCategoria,
    GestionarProducto,
    GestionarProveedor,
)
from core.application.catalog.movimientos import RegistrarEntrada, RegistrarSalida
from core.domain.shared.errors import DomainError, PermissionDeniedError

from infrastructure.django.unit_of_work import DjangoUnitOfWork

from apps.accounts.permissions import EsAdministrador, EsAdministradorOVendedor
from apps.catalog.queries import (
    alertas_stock,
    categorias_de,
    historial_entradas,
    historial_movimientos,
    listar_inventario,
    parse_fecha,
    productos_mas_vendidos,
    productos_para_historial,
    productos_vendidos,
    resumen_hoy,
    resumen_periodo,
)
from apps.common.exceptions import responder_domain_error


def _uow() -> DjangoUnitOfWork:
    return DjangoUnitOfWork()


def _admin_id(request, uow: DjangoUnitOfWork) -> int:
    if request.user.rol == "administrador":
        return request.user.id
    vinculos = uow.vinculos.listar_por_vendedor(request.user.id)
    aceptados = [vinculo for vinculo in vinculos if vinculo.estado.value == "aceptado"]
    if not aceptados:
        raise PermissionDeniedError(
            "El vendedor no tiene un administrador con vínculo aceptado"
        )
    solicitado = request.data.get("admin_id") or request.query_params.get("admin_id")
    if solicitado:
        for vinculo in aceptados:
            if str(vinculo.administrador_id) == str(solicitado):
                return vinculo.administrador_id
        raise PermissionDeniedError("El vínculo indicado no está aceptado")
    return aceptados[0].administrador_id


def _producto_payload(uow: DjangoUnitOfWork, producto) -> dict:
    from core.domain.shared.enums import TipoCliente

    stock = uow.movimientos.calcular_stock(producto.id, producto.administrador_id)
    precio = uow.precios.obtener_vigente(
        producto.id, producto.administrador_id, TipoCliente.INDIVIDUAL
    )
    return {
        "id": producto.id,
        "nombre": producto.nombre.valor,
        "categoria": producto.categoria_id,
        "precio_unitario": float(precio.precio.amount) if precio else 0.0,
        "stock_minimo": float(producto.stock_minimo.valor),
        "stock_actual": float(stock),
        "activo": True,
    }


def _categoria_payload(categoria) -> dict:
    return {"id": categoria.id, "nombre": categoria.nombre.valor}


def _proveedor_payload(proveedor) -> dict:
    return {
        "id": proveedor.id,
        "nombre": proveedor.nombre,
        "contacto": proveedor.contacto,
        "activo": True,
    }


class CategoriaSelectView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def get(self, request):
        with _uow() as uow:
            admin_id = _admin_id(request, uow)
            return Response(categorias_de(admin_id))


class CategoriaCreateView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request):
        nombre = str(request.data.get("nombre") or "").strip()
        if not nombre:
            return Response(
                {"detail": "El nombre es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with _uow() as uow:
                categoria = GestionarCategoria(uow).crear(request.user.id, nombre)
                return Response(_categoria_payload(categoria), status=status.HTTP_201_CREATED)
        except DomainError as exc:
            return responder_domain_error(exc)
        except IntegrityError:
            return Response(
                {"detail": "Ya existe una categoría con ese nombre"},
                status=status.HTTP_409_CONFLICT,
            )


class CategoriaDetailView(APIView):
    permission_classes = [EsAdministrador]

    def put(self, request, categoria_id: int):
        return self._actualizar(request, categoria_id)

    def patch(self, request, categoria_id: int):
        return self._actualizar(request, categoria_id)

    def _actualizar(self, request, categoria_id: int):
        nombre = str(request.data.get("nombre") or "").strip()
        if not nombre:
            return Response(
                {"detail": "El nombre es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with _uow() as uow:
                categoria = GestionarCategoria(uow).actualizar(
                    request.user.id, categoria_id, nombre
                )
                return Response(_categoria_payload(categoria))
        except DomainError as exc:
            return responder_domain_error(exc)
        except IntegrityError:
            return Response(
                {"detail": "Ya existe una categoría con ese nombre"},
                status=status.HTTP_409_CONFLICT,
            )

    def delete(self, request, categoria_id: int):
        try:
            with _uow() as uow:
                GestionarCategoria(uow).eliminar(request.user.id, categoria_id)
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ProtectedError):
            return Response(
                {"detail": "No se puede eliminar una categoría con productos asociados"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductoListCreateView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def get(self, request):
        with _uow() as uow:
            admin_id = _admin_id(request, uow)
            return Response(listar_inventario(admin_id))

    def post(self, request):
        if request.user.rol != "administrador":
            raise PermissionDeniedError("Solo un administrador puede crear productos")
        try:
            with _uow() as uow:
                producto = GestionarProducto(uow).crear(
                    administrador_id=request.user.id,
                    usuario_id=request.user.id,
                    nombre=str(request.data.get("nombre") or ""),
                    categoria_id=int(request.data.get("categoria") or 0),
                    precio=request.data.get("precio_unitario"),
                    stock_minimo=request.data.get("stock_minimo") or 0,
                    cantidad_inicial=request.data.get("cantidad_inicial") or 0,
                )
                return Response(
                    _producto_payload(uow, producto), status=status.HTTP_201_CREATED
                )
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ValueError, TypeError):
            return Response(
                {"detail": "No se pudo crear el producto. Revisá los datos."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProductoDetailView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request, producto_id: int):
        with _uow() as uow:
            producto = uow.productos.obtener_por_id(producto_id)
            if producto is None or producto.administrador_id != request.user.id:
                return Response(
                    {"detail": "El producto no existe"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(_producto_payload(uow, producto))

    def put(self, request, producto_id: int):
        return self._actualizar(request, producto_id)

    def patch(self, request, producto_id: int):
        return self._actualizar(request, producto_id)

    def _actualizar(self, request, producto_id: int):
        try:
            with _uow() as uow:
                producto = GestionarProducto(uow).actualizar(
                    administrador_id=request.user.id,
                    producto_id=producto_id,
                    nombre=request.data.get("nombre"),
                    categoria_id=(
                        int(request.data.get("categoria"))
                        if request.data.get("categoria") is not None
                        else None
                    ),
                    precio=request.data.get("precio_unitario"),
                    stock_minimo=request.data.get("stock_minimo"),
                )
                return Response(_producto_payload(uow, producto))
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ValueError, TypeError):
            return Response(
                {"detail": "No se pudo actualizar el producto. Revisá los datos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, producto_id: int):
        try:
            with _uow() as uow:
                GestionarProducto(uow).eliminar(request.user.id, producto_id)
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ProtectedError):
            return Response(
                {"detail": "No se puede eliminar un producto con movimientos asociados"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductoAlertasView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def get(self, request):
        with _uow() as uow:
            admin_id = _admin_id(request, uow)
            return Response(alertas_stock(admin_id))


class ProductoMasVendidosView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        return Response(productos_mas_vendidos(request.user.id))


class ProductosVendidosView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        desde = parse_fecha(request.query_params.get("desde"))
        hasta = parse_fecha(request.query_params.get("hasta"))
        if desde is None or hasta is None:
            return Response(
                {"detail": "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(productos_vendidos(request.user.id, desde, hasta))


class ProveedorSelectView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        with _uow() as uow:
            proveedores = uow.proveedores.listar_por_administrador(request.user.id)
            return Response([_proveedor_payload(proveedor) for proveedor in proveedores])

    def post(self, request):
        nombre = str(request.data.get("nombre") or "").strip()
        contacto = str(request.data.get("contacto") or "").strip() or None
        if not nombre:
            return Response(
                {"detail": "El nombre es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with _uow() as uow:
                proveedor = GestionarProveedor(uow).crear(
                    request.user.id, nombre, contacto
                )
                return Response(
                    _proveedor_payload(proveedor), status=status.HTTP_201_CREATED
                )
        except DomainError as exc:
            return responder_domain_error(exc)


class ProveedorDetailView(APIView):
    permission_classes = [EsAdministrador]

    def put(self, request, proveedor_id: int):
        return self._actualizar(request, proveedor_id)

    def patch(self, request, proveedor_id: int):
        return self._actualizar(request, proveedor_id)

    def _actualizar(self, request, proveedor_id: int):
        try:
            with _uow() as uow:
                proveedor = GestionarProveedor(uow).actualizar(
                    request.user.id,
                    proveedor_id,
                    nombre=request.data.get("nombre"),
                    contacto=request.data.get("contacto"),
                )
                return Response(_proveedor_payload(proveedor))
        except DomainError as exc:
            return responder_domain_error(exc)

    def delete(self, request, proveedor_id: int):
        try:
            with _uow() as uow:
                GestionarProveedor(uow).eliminar(request.user.id, proveedor_id)
        except DomainError as exc:
            return responder_domain_error(exc)
        except (IntegrityError, ProtectedError):
            return Response(
                {"detail": "No se puede eliminar un proveedor con compras asociadas"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResumenHoyView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        return Response(resumen_hoy(request.user.id))


class ResumenPeriodoView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        desde = parse_fecha(request.query_params.get("desde"))
        hasta = parse_fecha(request.query_params.get("hasta"))
        if desde is None or hasta is None:
            return Response(
                {"detail": "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(resumen_periodo(request.user.id, desde, hasta))


class RegistrarEntradaView(APIView):
    permission_classes = [EsAdministrador]

    def post(self, request):
        try:
            with _uow() as uow:
                compra, stock = RegistrarEntrada(uow).ejecutar(
                    administrador_id=request.user.id,
                    usuario_id=request.user.id,
                    producto_id=int(request.data.get("producto") or 0),
                    proveedor_id=int(request.data.get("proveedor") or 0),
                    cantidad=request.data.get("cantidad"),
                    costo_unitario=request.data.get("costo_unitario") or 0,
                )
                producto = uow.productos.obtener_por_id(compra.lineas[0].producto_id)
                proveedor = uow.proveedores.obtener_por_id(compra.proveedor_id)
                return Response(
                    {
                        "mensaje": "Entrada registrada correctamente.",
                        "compra_id": compra.id,
                        "producto_id": compra.lineas[0].producto_id,
                        "producto": producto.nombre.valor if producto else "—",
                        "cantidad": float(compra.lineas[0].cantidad.value),
                        "proveedor": proveedor.nombre if proveedor else "—",
                        "nuevo_stock": float(stock),
                    },
                    status=status.HTTP_201_CREATED,
                )
        except DomainError as exc:
            return responder_domain_error(exc)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Revisá el producto, el proveedor y la cantidad."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegistrarSalidaView(APIView):
    permission_classes = [EsAdministradorOVendedor]

    def post(self, request):
        try:
            with _uow() as uow:
                admin_id = _admin_id(request, uow)
                venta, stock = RegistrarSalida(uow).ejecutar(
                    administrador_id=admin_id,
                    vendedor_id=request.user.id,
                    producto_id=int(request.data.get("producto") or 0),
                    cantidad=request.data.get("cantidad"),
                    canal_venta=str(request.data.get("canal_venta") or ""),
                )
                producto = uow.productos.obtener_por_id(venta.lineas[0].producto_id)
                return Response(
                    {
                        "mensaje": "Venta registrada correctamente.",
                        "venta_id": venta.id,
                        "producto_id": venta.lineas[0].producto_id,
                        "producto": producto.nombre.valor if producto else "—",
                        "cantidad": float(venta.lineas[0].cantidad.value),
                        "canal_venta": (
                            venta.canal_venta.value if venta.canal_venta else None
                        ),
                        "nuevo_stock": float(stock),
                    },
                    status=status.HTTP_201_CREATED,
                )
        except DomainError as exc:
            return responder_domain_error(exc)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Revisá el producto, la cantidad y el canal de venta."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class HistorialEntradasView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        return Response(historial_entradas(request.user.id))


class HistorialMovimientosView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request, limite: int):
        return Response(historial_movimientos(request.user.id, limite))


class ProductosHistoryView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        return Response(productos_para_historial(request.user.id))


class ReportePeriodoPDFView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        desde = parse_fecha(request.query_params.get("desde"))
        hasta = parse_fecha(request.query_params.get("hasta"))
        if desde is None or hasta is None:
            return Response(
                {"detail": "Los parámetros 'desde' y 'hasta' son obligatorios (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resumen = resumen_periodo(request.user.id, desde, hasta)
        productos = productos_vendidos(request.user.id, desde, hasta)

        try:
            from weasyprint import HTML
        except Exception:
            return Response(
                {"detail": "La exportación a PDF no está disponible en este servidor."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        html = render_to_string(
            "inventario/reporte_periodo_pdf.html",
            {
                "desde": desde.isoformat(),
                "hasta": hasta.isoformat(),
                "resumen": resumen,
                "productos": productos,
            },
        )
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_{desde.isoformat()}_{hasta.isoformat()}.pdf"'
        )
        return response
