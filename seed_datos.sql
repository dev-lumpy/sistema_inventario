-- ============================================================
-- Datos de ejemplo para SistemaTaller
-- Ejecutar con: sqlite3 db.sqlite3 < seed_datos.sql
-- Es idempotente para categorias/proveedores/productos y para
-- los movimientos identificados por su detalle.
-- ============================================================

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- ---------- Categorías ----------
INSERT OR IGNORE INTO inventario_categoria (nombre) VALUES
  ('Lubricantes'),
  ('Filtros'),
  ('Frenos'),
  ('Baterías'),
  ('Neumáticos'),
  ('Suspensión'),
  ('Motor'),
  ('Eléctrico'),
  ('Accesorios'),
  ('Herramientas');

-- ---------- Proveedores ----------
INSERT OR IGNORE INTO inventario_proveedor (nombre, contacto, telefono, email, activo) VALUES
  ('AutoPartes del Norte', 'Juan Pérez',  '381-555-1001', 'ventas@autopartesnorte.com', 1),
  ('LubriMax SRL',         'Carla Gómez', '381-555-1002', 'pedidos@lubrimax.com',       1),
  ('Filtros Argentinos',   'Martín Díaz', '381-555-1003', 'ventas@filtrosarg.com',      1),
  ('Baterías Central',     'Lucía Romero','381-555-1004', 'contacto@bateriascentral.com',1),
  ('Neumáticos Sur',       'Diego Fernández','381-555-1005','info@neumaticossur.com',   1);

-- ---------- Productos ----------
CREATE TEMP TABLE _seed_producto (
  nombre       TEXT,
  categoria    TEXT,
  precio       REAL,
  stock_minimo INTEGER,
  activo       INTEGER
);

INSERT INTO _seed_producto (nombre, categoria, precio, stock_minimo, activo) VALUES
  ('Aceite 20W-50 Mineral 5L',      'Lubricantes',  18500.00, 10, 1),
  ('Aceite 10W-40 Sintético 4L',    'Lubricantes',  32000.00,  8, 1),
  ('Grasa Multiuso 1kg',            'Lubricantes',   9500.00,  6, 1),
  ('Líquido de Frenos DOT4 500ml',  'Lubricantes',   7800.00, 12, 1),
  ('Filtro de Aceite Universal',    'Filtros',       6500.00, 15, 1),
  ('Filtro de Aire Deportivo',      'Filtros',      12000.00, 10, 1),
  ('Filtro de Combustible Diesel',  'Filtros',       9800.00, 10, 1),
  ('Pastillas de Freno Delanteras', 'Frenos',       24500.00,  8, 1),
  ('Disco de Freno Ventilado',      'Frenos',       48000.00,  4, 1),
  ('Kit de Zapatas Traseras',       'Frenos',       27500.00,  5, 1),
  ('Batería 12V 65Ah',              'Baterías',     95000.00,  3, 1),
  ('Batería 12V 80Ah',              'Baterías',    125000.00,  2, 1),
  ('Neumático 185/65 R15',          'Neumáticos',   78000.00,  4, 1),
  ('Neumático 205/55 R16',          'Neumáticos',   98000.00,  4, 1),
  ('Amortiguador Delantero',        'Suspensión',   42000.00,  4, 1),
  ('Rótula de Suspensión',          'Suspensión',   15500.00,  6, 1),
  ('Bujía de Iridio',               'Motor',         8900.00, 20, 1),
  ('Correa de Distribución',        'Motor',        36000.00,  5, 1),
  ('Lámpara H4 LED',                'Eléctrico',    14500.00, 10, 1),
  ('Fusible 15A (pack x10)',         'Eléctrico',     3200.00, 15, 1),
  ('Kit de Limpieza Interior',      'Accesorios',   11500.00,  5, 1),
  ('Funda Cubre Auto',              'Accesorios',   28000.00,  3, 1),
  ('Llave de Tuercas Cruz',         'Herramientas', 13200.00,  4, 1),
  ('Gato Hidráulico 2T',            'Herramientas', 56000.00,  3, 1);

INSERT INTO inventario_producto (nombre, precio_unitario, stock_minimo, creado, categoria_id, activo)
SELECT s.nombre, s.precio, s.stock_minimo, datetime('now', '-45 days'), c.id, s.activo
FROM _seed_producto s
JOIN inventario_categoria c ON c.nombre = s.categoria
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_producto p WHERE p.nombre = s.nombre
);

DROP TABLE _seed_producto;

-- ---------- Movimientos: stock inicial ----------
CREATE TEMP TABLE _seed_inicial (nombre TEXT, cantidad INTEGER);

INSERT INTO _seed_inicial (nombre, cantidad) VALUES
  ('Aceite 20W-50 Mineral 5L', 40),
  ('Aceite 10W-40 Sintético 4L', 25),
  ('Grasa Multiuso 1kg', 18),
  ('Líquido de Frenos DOT4 500ml', 30),
  ('Filtro de Aceite Universal', 60),
  ('Filtro de Aire Deportivo', 22),
  ('Filtro de Combustible Diesel', 35),
  ('Pastillas de Freno Delanteras', 20),
  ('Disco de Freno Ventilado', 10),
  ('Kit de Zapatas Traseras', 12),
  ('Batería 12V 65Ah', 8),
  ('Batería 12V 80Ah', 5),
  ('Neumático 185/65 R15', 16),
  ('Neumático 205/55 R16', 12),
  ('Amortiguador Delantero', 10),
  ('Rótula de Suspensión', 14),
  ('Bujía de Iridio', 80),
  ('Correa de Distribución', 9),
  ('Lámpara H4 LED', 24),
  ('Fusible 15A (pack x10)', 50),
  ('Kit de Limpieza Interior', 15),
  ('Funda Cubre Auto', 7),
  ('Llave de Tuercas Cruz', 10),
  ('Gato Hidráulico 2T', 6);

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'E', s.cantidad, datetime('now', '-40 days'), p.id, 'Carga inicial', 'inicial', NULL, NULL
FROM _seed_inicial s
JOIN inventario_producto p ON p.nombre = s.nombre
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock m
  WHERE m.producto_id = p.id AND m.motivo = 'inicial' AND m.detalle = 'Carga inicial'
);

DROP TABLE _seed_inicial;

-- ---------- Movimientos: compras a proveedor ----------
CREATE TEMP TABLE _seed_compra (
  producto  TEXT,
  cantidad  INTEGER,
  proveedor TEXT,
  detalle   TEXT,
  dias      INTEGER
);

INSERT INTO _seed_compra (producto, cantidad, proveedor, detalle, dias) VALUES
  ('Aceite 20W-50 Mineral 5L',      20, 'LubriMax SRL',        'Factura A-1001', 20),
  ('Filtro de Aceite Universal',    30, 'Filtros Argentinos',  'Factura A-1002', 18),
  ('Batería 12V 65Ah',               4, 'Baterías Central',    'Factura A-1003', 12),
  ('Neumático 185/65 R15',           8, 'Neumáticos Sur',      'Factura A-1004',  9),
  ('Bujía de Iridio',               40, 'AutoPartes del Norte','Factura A-1005',  6);

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'E', c.cantidad, datetime('now', '-' || c.dias || ' days'), p.id, c.detalle, 'compra', pr.id, NULL
FROM _seed_compra c
JOIN inventario_producto p ON p.nombre = c.producto
JOIN inventario_proveedor pr ON pr.nombre = c.proveedor
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock m
  WHERE m.producto_id = p.id AND m.motivo = 'compra' AND m.detalle = c.detalle
);

DROP TABLE _seed_compra;

-- ---------- Movimientos: ventas (salidas) ----------
CREATE TEMP TABLE _seed_venta (
  producto TEXT,
  cantidad INTEGER,
  canal    TEXT,
  detalle  TEXT,
  dias     INTEGER
);

INSERT INTO _seed_venta (producto, cantidad, canal, detalle, dias) VALUES
  ('Aceite 20W-50 Mineral 5L',      5, 'whatsapp',   'Venta WhatsApp #101',   5),
  ('Filtro de Aceite Universal',    8, 'presencial', 'Venta mostrador #102',  4),
  ('Pastillas de Freno Delanteras', 3, 'instagram',  'Venta Instagram #103',  3),
  ('Batería 12V 65Ah',              2, 'facebook',   'Venta Facebook #104',   2),
  ('Neumático 185/65 R15',          3, 'presencial', 'Venta mostrador #105',  2),
  ('Bujía de Iridio',              15, 'whatsapp',   'Venta WhatsApp #106',   1),
  ('Lámpara H4 LED',                4, 'otro',       'Venta otro #107',       1);

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'S', v.cantidad, datetime('now', '-' || v.dias || ' days'), p.id, v.detalle, 'venta', NULL, v.canal
FROM _seed_venta v
JOIN inventario_producto p ON p.nombre = v.producto
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock m
  WHERE m.producto_id = p.id AND m.motivo = 'venta' AND m.detalle = v.detalle
);

DROP TABLE _seed_venta;

-- ---------- Movimientos: mermas (salidas) ----------
CREATE TEMP TABLE _seed_merma (
  producto TEXT,
  cantidad INTEGER,
  detalle  TEXT,
  dias     INTEGER
);

INSERT INTO _seed_merma (producto, cantidad, detalle, dias) VALUES
  ('Grasa Multiuso 1kg',            1, 'Merma: producto vencido',  7),
  ('Filtro de Combustible Diesel',  2, 'Merma: empaque dañado',    5),
  ('Fusible 15A (pack x10)',        5, 'Merma: piezas rotas',      4);

INSERT INTO inventario_movimientostock
  (tipo, cantidad, fecha, producto_id, detalle, motivo, proveedor_id, canal_venta)
SELECT 'S', m.cantidad, datetime('now', '-' || m.dias || ' days'), p.id, m.detalle, 'merma', NULL, NULL
FROM _seed_merma m
JOIN inventario_producto p ON p.nombre = m.producto
WHERE NOT EXISTS (
  SELECT 1 FROM inventario_movimientostock x
  WHERE x.producto_id = p.id AND x.motivo = 'merma' AND x.detalle = m.detalle
);

DROP TABLE _seed_merma;

COMMIT;
