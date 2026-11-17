from __future__ import annotations

from django.db import connections

from apps.accounts.models import (
    Administrador,
    Usuario,
    Vendedor,
    VendedorAdministrador,
)
from apps.catalog.models import (
    Categoria,
    MovimientoInventario,
    PrecioProducto,
    Producto,
)
from apps.payments.models import Pago
from apps.purchases.models import Compra, CompraDetalle, Proveedor
from apps.sales.models import Venta, VentaDetalle

MODELOS_EN_ORDEN = [
    Usuario,
    Administrador,
    Vendedor,
    VendedorAdministrador,
    Categoria,
    Producto,
    PrecioProducto,
    Proveedor,
    Compra,
    CompraDetalle,
    Venta,
    VentaDetalle,
    MovimientoInventario,
    Pago,
]

TRIGGERS = [
    (
        "trg_total_venta_insert",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_venta_insert
        AFTER INSERT ON venta_detalle
        BEGIN
            UPDATE ventas
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM venta_detalle
                WHERE venta_id = NEW.venta_id
            )
            WHERE id = NEW.venta_id;
        END;
        """,
    ),
    (
        "trg_total_venta_update",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_venta_update
        AFTER UPDATE ON venta_detalle
        BEGIN
            UPDATE ventas
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM venta_detalle
                WHERE venta_id = NEW.venta_id
            )
            WHERE id = NEW.venta_id;
        END;
        """,
    ),
    (
        "trg_total_venta_delete",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_venta_delete
        AFTER DELETE ON venta_detalle
        BEGIN
            UPDATE ventas
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM venta_detalle
                WHERE venta_id = OLD.venta_id
            )
            WHERE id = OLD.venta_id;
        END;
        """,
    ),
    (
        "trg_total_compra_insert",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_compra_insert
        AFTER INSERT ON compra_detalle
        BEGIN
            UPDATE compras
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM compra_detalle
                WHERE compra_id = NEW.compra_id
            )
            WHERE id = NEW.compra_id;
        END;
        """,
    ),
    (
        "trg_total_compra_update",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_compra_update
        AFTER UPDATE ON compra_detalle
        BEGIN
            UPDATE compras
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM compra_detalle
                WHERE compra_id = NEW.compra_id
            )
            WHERE id = NEW.compra_id;
        END;
        """,
    ),
    (
        "trg_total_compra_delete",
        """
        CREATE TRIGGER IF NOT EXISTS trg_total_compra_delete
        AFTER DELETE ON compra_detalle
        BEGIN
            UPDATE compras
            SET total = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM compra_detalle
                WHERE compra_id = OLD.compra_id
            )
            WHERE id = OLD.compra_id;
        END;
        """,
    ),
    (
        "trg_movimiento_venta",
        """
        CREATE TRIGGER IF NOT EXISTS trg_movimiento_venta
        AFTER UPDATE OF estado ON ventas
        WHEN NEW.estado = 'confirmada' AND OLD.estado <> 'confirmada'
        BEGIN
            INSERT INTO movimiento_inventario
                (administrador_id, producto_id, motivo, cantidad, fecha,
                 precio_unitario, referencia_tipo, referencia_id, usuario_id, nota)
            SELECT vd.administrador_id, vd.producto_id, 'venta', vd.cantidad,
                   CURRENT_TIMESTAMP, vd.precio_unitario, 'venta', NEW.id,
                   NEW.vendedor_id, NULL
            FROM venta_detalle vd
            WHERE vd.venta_id = NEW.id;
        END;
        """,
    ),
    (
        "trg_movimiento_compra",
        """
        CREATE TRIGGER IF NOT EXISTS trg_movimiento_compra
        AFTER UPDATE OF estado ON compras
        WHEN NEW.estado = 'confirmada' AND OLD.estado <> 'confirmada'
        BEGIN
            INSERT INTO movimiento_inventario
                (administrador_id, producto_id, motivo, cantidad, fecha,
                 costo_unitario, referencia_tipo, referencia_id, usuario_id, nota)
            SELECT cd.administrador_id, cd.producto_id, 'compra', cd.cantidad,
                   CURRENT_TIMESTAMP, cd.costo_unitario, 'compra', NEW.id,
                   NEW.usuario_id, NULL
            FROM compra_detalle cd
            WHERE cd.compra_id = NEW.id;
        END;
        """,
    ),
    (
        "trg_no_borrar_venta_confirmada",
        """
        CREATE TRIGGER IF NOT EXISTS trg_no_borrar_venta_confirmada
        BEFORE DELETE ON ventas
        WHEN OLD.estado = 'confirmada'
        BEGIN
            SELECT RAISE(ABORT, 'No se puede borrar una venta confirmada');
        END;
        """,
    ),
    (
        "trg_no_borrar_compra_confirmada",
        """
        CREATE TRIGGER IF NOT EXISTS trg_no_borrar_compra_confirmada
        BEFORE DELETE ON compras
        WHEN OLD.estado = 'confirmada'
        BEGIN
            SELECT RAISE(ABORT, 'No se puede borrar una compra confirmada');
        END;
        """,
    ),
]


def ensure_sqlite_schema(using: str = "default") -> bool:
    connection = connections[using]
    if connection.vendor != "sqlite":
        return False

    existentes = set(connection.introspection.table_names())
    with connection.schema_editor() as editor:
        for modelo in MODELOS_EN_ORDEN:
            tabla = modelo._meta.db_table
            if tabla not in existentes:
                editor.create_model(modelo)
                existentes.add(tabla)

    columnas_nuevas = {
        "administradores": ("moneda", "varchar(3) NOT NULL DEFAULT 'BOB'"),
        "ventas": ("moneda", "varchar(3) NOT NULL DEFAULT 'BOB'"),
        "compras": ("moneda", "varchar(3) NOT NULL DEFAULT 'BOB'"),
        "pagos": ("moneda", "varchar(3) NOT NULL DEFAULT 'BOB'"),
    }

    with connection.cursor() as cursor:
        for tabla, (columna, definicion) in columnas_nuevas.items():
            if tabla not in existentes:
                continue
            columnas = {
                col.name
                for col in connection.introspection.get_table_description(
                    cursor, tabla
                )
            }
            if columna not in columnas:
                cursor.execute(
                    f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}"
                )

        for _, sql in TRIGGERS:
            cursor.execute(sql)

    return True
