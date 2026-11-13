import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.apps import apps as django_apps
from django.conf import settings
from django.db import connection
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce

from apps.inventario.models import Categoria, MovimientoStock, Producto, Proveedor
from apps.usuarios.models import UsuarioORM, VendedorORM

st.set_page_config(page_title="Estado del inventario", layout="wide")

COLUMNAS_PRODUCTOS = [
    "Producto",
    "Categoría",
    "Precio",
    "Stock",
    "Stock mínimo",
    "Alerta",
    "Activo",
]
COLUMNAS_MOVIMIENTOS = [
    "Fecha",
    "Producto",
    "Tipo",
    "Motivo",
    "Cantidad",
    "Proveedor",
    "Detalle",
]
COLUMNAS_USUARIOS = ["Usuario", "Email", "Rol", "Estado", "Administrador", "Creado"]


@st.cache_data(ttl=10, show_spinner=False)
def cargar_estado():
    productos = list(
        Producto.objects.select_related("categoria")
        .annotate(
            entradas=Coalesce(
                Sum("movimientos__cantidad", filter=Q(movimientos__tipo="E")), 0
            ),
            salidas=Coalesce(
                Sum("movimientos__cantidad", filter=Q(movimientos__tipo="S")), 0
            ),
        )
        .annotate(stock=F("entradas") - F("salidas"))
        .order_by("nombre")
    )
    productos_df = pd.DataFrame(
        [
            {
                "Producto": p.nombre,
                "Categoría": p.categoria.nombre,
                "Precio": float(p.precio_unitario),
                "Stock": p.stock,
                "Stock mínimo": p.stock_minimo,
                "Alerta": "Sí" if p.stock <= p.stock_minimo else "No",
                "Activo": "Sí" if p.activo else "No",
            }
            for p in productos
        ],
        columns=COLUMNAS_PRODUCTOS,
    )

    movimientos = (
        MovimientoStock.objects.select_related("producto", "proveedor")
        .order_by("-fecha")
    )
    movimientos_df = pd.DataFrame(
        [
            {
                "Fecha": m.fecha,
                "Producto": m.producto.nombre,
                "Tipo": m.get_tipo_display(),
                "Motivo": m.get_motivo_display(),
                "Cantidad": m.cantidad,
                "Proveedor": m.proveedor.nombre if m.proveedor else "",
                "Detalle": m.detalle,
            }
            for m in movimientos
        ],
        columns=COLUMNAS_MOVIMIENTOS,
    )
    if not movimientos_df.empty:
        movimientos_df["Fecha"] = pd.to_datetime(movimientos_df["Fecha"])

    admin_por_vendedor = {
        v.pk: ", ".join(a.username for a in v.admins.all())
        for v in VendedorORM.objects.prefetch_related("admins")
    }
    usuarios_df = pd.DataFrame(
        [
            {
                "Usuario": u.username,
                "Email": u.email,
                "Rol": u.rol,
                "Estado": u.activo,
                "Administrador": admin_por_vendedor.get(u.pk, ""),
                "Creado": u.fecha_creacion,
            }
            for u in UsuarioORM.objects.all().order_by("username")
        ],
        columns=COLUMNAS_USUARIOS,
    )

    categorias_df = pd.DataFrame(
        [
            {"Categoría": c.nombre, "Productos": c.total_productos}
            for c in Categoria.objects.annotate(total_productos=Count("productos")).order_by(
                "nombre"
            )
        ],
        columns=["Categoría", "Productos"],
    )

    proveedores_df = pd.DataFrame(
        [
            {
                "Proveedor": p.nombre,
                "Contacto": p.contacto,
                "Teléfono": p.telefono,
                "Email": p.email,
                "Activo": "Sí" if p.activo else "No",
                "Movimientos": p.total_movimientos,
            }
            for p in Proveedor.objects.annotate(
                total_movimientos=Count("movimientos")
            ).order_by("nombre")
        ],
        columns=["Proveedor", "Contacto", "Teléfono", "Email", "Activo", "Movimientos"],
    )

    return {
        "productos": productos_df,
        "movimientos": movimientos_df,
        "usuarios": usuarios_df,
        "categorias": categorias_df,
        "proveedores": proveedores_df,
    }


@st.cache_data(ttl=10, show_spinner=False)
def tablas_y_migraciones():
    from django.db.migrations.executor import MigrationExecutor

    tablas = set(connection.introspection.table_names())
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    pendientes = [f"{migracion.app_label}.{migracion.name}" for migracion, retro in plan if not retro]
    return tablas, pendientes


def modelos_dominio():
    return [
        m
        for m in django_apps.get_models()
        if m._meta.app_label in {"inventario", "usuarios"}
    ]


def mostrar_tabla(df, columnas=None):
    if df.empty:
        st.info("No hay registros para mostrar.")
        return
    st.dataframe(df[columnas] if columnas else df, width="stretch")


try:
    estado = cargar_estado()
except Exception as exc:
    st.error("No se pudo leer la base de datos del proyecto.")
    st.code(str(exc))
    st.info("Revisá que el entorno sea el correcto y que las migraciones estén aplicadas: python manage.py migrate")
    st.stop()

productos = estado["productos"]
movimientos = estado["movimientos"]
usuarios = estado["usuarios"]
categorias = estado["categorias"]
proveedores = estado["proveedores"]

en_alerta = productos[productos["Alerta"] == "Sí"]
admins = usuarios[usuarios["Rol"] == "administrador"]
vendedores = usuarios[usuarios["Rol"] == "vendedor"]
stock_total = int(productos["Stock"].sum()) if not productos.empty else 0

st.title("Estado del proyecto — Sistema de Gestión de Inventario")
st.caption("Vista de solo lectura: no crea, modifica ni elimina datos.")

with st.sidebar:
    st.subheader("Entorno")
    st.write(f"**Motor:** {settings.DATABASES['default']['ENGINE']}")
    st.write(f"**Base de datos:** {settings.DATABASES['default']['NAME']}")
    st.write(f"**Django:** {django.get_version()}")
    st.write(f"**DEBUG:** {settings.DEBUG}")
    if st.button("Actualizar datos", width="stretch"):
        cargar_estado.clear()
        tablas_y_migraciones.clear()
        st.rerun()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Productos", len(productos))
col2.metric("En alerta", len(en_alerta))
col3.metric("Unidades en stock", stock_total)
col4.metric("Movimientos", len(movimientos))
col5.metric("Usuarios", len(usuarios))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Categorías", len(categorias))
col2.metric("Proveedores", len(proveedores))
col3.metric("Administradores", len(admins))
col4.metric("Vendedores", len(vendedores))

tab_resumen, tab_productos, tab_movimientos, tab_personas, tab_nodos = st.tabs(
    ["Resumen", "Productos", "Movimientos", "Personas", "Nodos del proyecto"]
)

with tab_resumen:
    izquierda, derecha = st.columns(2)
    with izquierda:
        st.subheader("Productos en alerta")
        if en_alerta.empty:
            st.success("Ningún producto está por debajo del stock mínimo.")
        else:
            mostrar_tabla(
                en_alerta[["Producto", "Categoría", "Stock", "Stock mínimo"]]
            )
    with derecha:
        st.subheader("Últimos movimientos")
        if movimientos.empty:
            st.info("Todavía no hay movimientos registrados.")
        else:
            mostrar_tabla(movimientos.head(10))

with tab_productos:
    filtro1, filtro2, filtro3 = st.columns([2, 1, 1])
    opciones_categoria = ["Todas"] + sorted(productos["Categoría"].unique().tolist())
    categoria = filtro1.selectbox("Categoría", opciones_categoria)
    solo_alerta = filtro2.checkbox("Solo alertas")
    solo_activos = filtro3.checkbox("Solo activos", value=True)

    filtrado = productos.copy()
    if categoria != "Todas":
        filtrado = filtrado[filtrado["Categoría"] == categoria]
    if solo_alerta:
        filtrado = filtrado[filtrado["Alerta"] == "Sí"]
    if solo_activos:
        filtrado = filtrado[filtrado["Activo"] == "Sí"]

    st.metric("Productos que coinciden", len(filtrado))
    mostrar_tabla(filtrado)
    if not filtrado.empty:
        serie = (
            filtrado.set_index("Producto")["Stock"]
            .sort_values(ascending=False)
            .head(20)
        )
        st.subheader("Stock por producto")
        st.bar_chart(serie, width="stretch")

with tab_movimientos:
    filtro1, filtro2 = st.columns(2)
    tipos = ["Todos"] + sorted(movimientos["Tipo"].unique().tolist())
    motivos = ["Todos"] + sorted(movimientos["Motivo"].unique().tolist())
    tipo = filtro1.selectbox("Tipo", tipos)
    motivo = filtro2.selectbox("Motivo", motivos)

    filtrado = movimientos.copy()
    if tipo != "Todos":
        filtrado = filtrado[filtrado["Tipo"] == tipo]
    if motivo != "Todos":
        filtrado = filtrado[filtrado["Motivo"] == motivo]

    st.metric("Movimientos que coinciden", len(filtrado))
    mostrar_tabla(filtrado)
    if not filtrado.empty:
        por_dia = (
            filtrado.assign(Día=filtrado["Fecha"].dt.date)
            .groupby(["Día", "Tipo"])
            .size()
            .unstack(fill_value=0)
        )
        st.subheader("Movimientos por día")
        st.bar_chart(por_dia, width="stretch")

with tab_personas:
    st.subheader("Usuarios del sistema")
    mostrar_tabla(usuarios)
    st.subheader("Proveedores")
    mostrar_tabla(proveedores)
    st.subheader("Categorías")
    mostrar_tabla(categorias)

with tab_nodos:
    st.subheader("Mapa de relaciones del dominio")
    st.graphviz_chart(
        """
        digraph proyecto {
            rankdir=LR;
            graph [bgcolor="transparent"];
            node [shape=box, style="rounded,filled", fillcolor="#eef2ff", color="#94a3b8", fontname="Helvetica"];
            edge [color="#64748b", fontname="Helvetica", fontsize=10];

            UsuarioORM [label="UsuarioORM\\nusuarios_usuario"];
            AdministradorORM [label="AdministradorORM\\nusuarios_administrador"];
            VendedorORM [label="VendedorORM\\nusuarios_vendedor"];
            Categoria [label="Categoria"];
            Producto [label="Producto"];
            MovimientoStock [label="MovimientoStock"];
            Proveedor [label="Proveedor"];

            UsuarioORM -> AdministradorORM;
            UsuarioORM -> VendedorORM;
            AdministradorORM -> VendedorORM [label="admin"];
            Categoria -> Producto [label="categoria"];
            Producto -> MovimientoStock [label="movimientos"];
            Proveedor -> MovimientoStock [label="proveedor"];
        }
        """,
        width="stretch",
    )

    st.subheader("Estado de las tablas")
    filas = []
    for modelo in modelos_dominio():
        try:
            registros = modelo.objects.count()
            estado_tabla = "Con datos" if registros else "Vacía"
        except Exception:
            registros = None
            estado_tabla = "No se pudo leer"
        filas.append(
            {
                "Modelo": modelo.__name__,
                "Tabla": modelo._meta.db_table,
                "Registros": registros,
                "Estado": estado_tabla,
            }
        )
    st.dataframe(pd.DataFrame(filas), width="stretch")

    try:
        tablas, pendientes = tablas_y_migraciones()
        requeridas = {modelo._meta.db_table for modelo in modelos_dominio()}
        faltantes = sorted(requeridas - tablas)
        if faltantes:
            st.warning(f"Faltan tablas en la base de datos: {', '.join(faltantes)}")
        else:
            st.success("Todas las tablas del dominio existen.")
        if pendientes:
            st.warning(f"Migraciones pendientes: {', '.join(pendientes)}")
        else:
            st.success("Migraciones al día.")
    except Exception as exc:
        st.info(f"No se pudo verificar el estado de migraciones: {exc}")
