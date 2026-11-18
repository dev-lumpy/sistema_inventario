-- Ejecutar despues de cargar seed_demo.sql directamente en PostgreSQL.
-- El comando `python manage.py seed_demo` ya hace esto automaticamente.

SELECT setval(pg_get_serial_sequence('usuarios', 'id'), (SELECT COALESCE(MAX(id), 1) FROM usuarios));
SELECT setval(pg_get_serial_sequence('categorias', 'id'), (SELECT COALESCE(MAX(id), 1) FROM categorias));
SELECT setval(pg_get_serial_sequence('productos', 'id'), (SELECT COALESCE(MAX(id), 1) FROM productos));
SELECT setval(pg_get_serial_sequence('precios_producto', 'id'), (SELECT COALESCE(MAX(id), 1) FROM precios_producto));
SELECT setval(pg_get_serial_sequence('proveedores', 'id'), (SELECT COALESCE(MAX(id), 1) FROM proveedores));
SELECT setval(pg_get_serial_sequence('compras', 'id'), (SELECT COALESCE(MAX(id), 1) FROM compras));
SELECT setval(pg_get_serial_sequence('compra_detalle', 'id'), (SELECT COALESCE(MAX(id), 1) FROM compra_detalle));
SELECT setval(pg_get_serial_sequence('ventas', 'id'), (SELECT COALESCE(MAX(id), 1) FROM ventas));
SELECT setval(pg_get_serial_sequence('venta_detalle', 'id'), (SELECT COALESCE(MAX(id), 1) FROM venta_detalle));
SELECT setval(pg_get_serial_sequence('movimiento_inventario', 'id'), (SELECT COALESCE(MAX(id), 1) FROM movimiento_inventario));
SELECT setval(pg_get_serial_sequence('pagos', 'id'), (SELECT COALESCE(MAX(id), 1) FROM pagos));
