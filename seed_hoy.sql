-- ============================================================
-- Movimientos de ejemplo para HOY (entradas + ventas)
-- y algunos productos dejados en alerta (stock <= stock_minimo).
-- Ejecutar con: sqlite3 db.sqlite3 < seed_hoy.sql
-- ============================================================

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- ---------- Entradas de hoy (compras a proveedor) ----------
CREATE TEMP TABLE _hoy_compra (
  producto  TEXT,
  cantidad  INTEGER,
  proveedor TEXT,
  detalle   TEXT
);

INSERT INTO _hoy_compra (producto, cantidad, proveedor, detalle) VALUES
  ('Aceite 20W-50 Mineral 5L',     10, 'LubriMax SRL',         'Factura A-2001'),
  ('Filtro de Aceite Universal',   20, 'Filtros Argentinos',   'Factura A-2002'),
  ('Bujía de Iridio',              30, 'AutoPartes del Norte', 'Factura A-2003'),
  ('Líquido de Frenos DOT4 500ml', 10, 'LubriMax SRL',         'Factura A-2004');

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'E', c.cantidad, datetime('now'), p.id, c.detalle, 'compra', pr.id, NULL
FROM _hoy_compra c
JOIN inventario_producto p ON p.nombre = c.producto
JOIN inventario_proveedor pr ON pr.nombre = c.proveedor
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock m
  WHERE m.producto_id = p.id AND m.motivo = 'compra' AND m.detalle = c.detalle
);

DROP TABLE _hoy_compra;

-- ---------- Ventas de hoy ----------
-- Incluye ventas que dejan en alerta a Batería 80Ah, Correa,
-- Gato Hidráulico, Funda Cubre Auto y Rótula.
CREATE TEMP TABLE _hoy_venta (
  producto TEXT,
  cantidad INTEGER,
  canal    TEXT,
  detalle  TEXT
);

INSERT INTO _hoy_venta (producto, cantidad, canal, detalle) VALUES
  ('Aceite 20W-50 Mineral 5L',      3, 'whatsapp',   'Venta WhatsApp #201'),
  ('Filtro de Aceite Universal',    6, 'presencial', 'Venta mostrador #202'),
  ('Pastillas de Freno Delanteras', 4, 'instagram',  'Venta Instagram #203'),
  ('Lámpara H4 LED',                5, 'facebook',   'Venta Facebook #204'),
  ('Batería 12V 80Ah',              3, 'presencial', 'Venta mostrador #205'),
  ('Correa de Distribución',        4, 'whatsapp',   'Venta WhatsApp #206'),
  ('Gato Hidráulico 2T',            3, 'otro',       'Venta otro #207'),
  ('Funda Cubre Auto',              4, 'instagram',  'Venta Instagram #208'),
  ('Rótula de Suspensión',          8, 'presencial', 'Venta mostrador #209');

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'S', v.cantidad, datetime('now'), p.id, v.detalle, 'venta', NULL, v.canal
FROM _hoy_venta v
JOIN inventario_producto p ON p.nombre = v.producto
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock m
  WHERE m.producto_id = p.id AND m.motivo = 'venta' AND m.detalle = v.detalle
);

DROP TABLE _hoy_venta;

COMMIT;
