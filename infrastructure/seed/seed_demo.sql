-- ============================================================
-- DATOS DE DEMOSTRACION
-- 2 administradores, 6 vendedores, 6 categorias, 20 productos,
-- 42 precios, 4 proveedores, 4 compras, 6 ventas, 44 movimientos
-- y 4 pagos.
--
-- Contraseña para todos los usuarios: Password123!
-- Ejecutar solo sobre una base sin datos de negocio.
-- ============================================================

-- ============================================================
-- USUARIOS
-- ============================================================
INSERT INTO usuarios (id, nombre, apellidos, user_name, correo, password_hash, debe_cambiar_password, activo, creado_en) VALUES
(1, 'Ana', 'Admin', 'admin1', 'admin1@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', false, true, '2026-08-01 09:00:00+00:00'),
(2, 'Luis', 'Admin', 'admin2', 'admin2@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', false, true, '2026-08-01 09:05:00+00:00'),
(3, 'Vera', 'Vendedora', 'vendedor1', 'vendedor1@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, true, '2026-08-15 10:00:00+00:00'),
(4, 'Vic', 'Vendedor', 'vendedor2', 'vendedor2@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, true, '2026-08-15 10:05:00+00:00'),
(5, 'Violeta', 'Vendedora', 'vendedor3', 'vendedor3@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, true, '2026-08-15 10:10:00+00:00'),
(6, 'Valeria', 'Vendedora', 'vendedor4', 'vendedor4@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, false, '2026-08-15 10:15:00+00:00'),
(7, 'Victor', 'Vendedor', 'vendedor5', 'vendedor5@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, true, '2026-08-15 10:20:00+00:00'),
(8, 'Vanesa', 'Vendedora', 'vendedor6', 'vendedor6@taller.com', 'pbkdf2_sha256$1000000$QuI1B12Uon4PwATtEcoawI$016C9f9l/sArtunNrgz94bgciYCgCw8fbmJzUQgWlC0=', true, true, '2026-08-15 10:25:00+00:00');

-- ============================================================
-- ADMINISTRADORES
-- ============================================================
INSERT INTO administradores (id, nombre_negocio, moneda) VALUES
(1, 'Taller Andino', 'BOB'),
(2, 'Electro Jardin', 'USD');

-- ============================================================
-- VENDEDORES
-- ============================================================
INSERT INTO vendedores (id, creado_por_admin, creado_en, bloqueado, motivo_bloqueo, bloqueado_en) VALUES
(3, 1, '2026-08-15 10:00:00+00:00', false, NULL, NULL),
(4, 1, '2026-08-15 10:05:00+00:00', false, NULL, NULL),
(5, 1, '2026-08-15 10:10:00+00:00', false, NULL, NULL),
(6, 1, '2026-08-15 10:15:00+00:00', true, 'Cuenta suspendida para pruebas', '2026-10-01 12:00:00+00:00'),
(7, 2, '2026-08-15 10:20:00+00:00', false, NULL, NULL),
(8, 2, '2026-08-15 10:25:00+00:00', false, NULL, NULL);

-- ============================================================
-- VINCULOS VENDEDOR / ADMINISTRADOR
-- ============================================================
INSERT INTO vendedor_administrador (vendedor_id, administrador_id, estado, solicitado_por, motivo_estado, creado_en, actualizado_en) VALUES
(3, 1, 'aceptado', 'admin', NULL, '2026-09-01 11:00:00+00:00', '2026-09-01 11:00:00+00:00'),
(4, 1, 'aceptado', 'vendedor', NULL, '2026-09-01 11:05:00+00:00', '2026-09-01 11:05:00+00:00'),
(5, 1, 'aceptado', 'admin', NULL, '2026-09-01 11:10:00+00:00', '2026-09-01 11:10:00+00:00'),
(6, 1, 'pendiente', 'vendedor', 'Quiero cubrir el turno tarde', '2026-09-10 14:00:00+00:00', '2026-09-10 14:00:00+00:00'),
(7, 2, 'aceptado', 'admin', NULL, '2026-09-02 09:30:00+00:00', '2026-09-02 09:30:00+00:00'),
(8, 2, 'aceptado', 'admin', NULL, '2026-09-02 09:35:00+00:00', '2026-09-02 09:35:00+00:00'),
(6, 2, 'rechazado', 'admin', 'Capacidad completa por ahora', '2026-09-11 10:00:00+00:00', '2026-09-11 10:00:00+00:00'),
(5, 2, 'inactivo', 'admin', 'Vinculo pausado temporalmente', '2026-09-12 10:00:00+00:00', '2026-10-01 10:00:00+00:00'),
(4, 2, 'pendiente', 'vendedor', 'Quiero sumar otro administrador', '2026-10-05 16:00:00+00:00', '2026-10-05 16:00:00+00:00');

-- ============================================================
-- CATEGORIAS
-- ============================================================
INSERT INTO categorias (id, administrador_id, nombre) VALUES
(1, 1, 'Materiales de construccion'),
(2, 1, 'Herramientas'),
(3, 1, 'Pinturas'),
(4, 2, 'Electrico'),
(5, 2, 'Plomeria'),
(6, 2, 'Jardin');

-- ============================================================
-- PRODUCTOS
-- ============================================================
INSERT INTO productos (id, administrador_id, categoria_id, nombre, stock_minimo, creado_en) VALUES
(1, 1, 1, 'Cemento Portland 50kg', 5.000, '2026-09-01 08:00:00+00:00'),
(2, 1, 1, 'Arena fina', 10.000, '2026-09-01 08:05:00+00:00'),
(3, 1, 1, 'Ladrillo hueco', 20.000, '2026-09-01 08:10:00+00:00'),
(4, 1, 2, 'Martillo carpintero', 2.000, '2026-09-01 08:15:00+00:00'),
(5, 1, 2, 'Taladro percutor', 1.000, '2026-09-01 08:20:00+00:00'),
(6, 1, 2, 'Sierra circular', 1.000, '2026-09-01 08:25:00+00:00'),
(7, 1, 3, 'Pintura blanca 20L', 3.000, '2026-09-01 08:30:00+00:00'),
(8, 1, 3, 'Pintura negra 20L', 3.000, '2026-09-01 08:35:00+00:00'),
(9, 1, 3, 'Brocha 4 pulgadas', 5.000, '2026-09-01 08:40:00+00:00'),
(10, 1, 3, 'Rodillo antigota', 5.000, '2026-09-01 08:45:00+00:00'),
(11, 2, 4, 'Cable 2x2.5mm', 10.000, '2026-09-01 09:00:00+00:00'),
(12, 2, 4, 'Tomacorriente doble', 5.000, '2026-09-01 09:05:00+00:00'),
(13, 2, 4, 'Foco LED 9W', 10.000, '2026-09-01 09:10:00+00:00'),
(14, 2, 5, 'Tubo PVC 2 pulgadas', 8.000, '2026-09-01 09:15:00+00:00'),
(15, 2, 5, 'Llave de paso', 4.000, '2026-09-01 09:20:00+00:00'),
(16, 2, 5, 'Codo PVC 2 pulgadas', 10.000, '2026-09-01 09:25:00+00:00'),
(17, 2, 6, 'Maceta 10L', 5.000, '2026-09-01 09:30:00+00:00'),
(18, 2, 6, 'Tierra fertil 5kg', 6.000, '2026-09-01 09:35:00+00:00'),
(19, 2, 6, 'Regadera 5L', 3.000, '2026-09-01 09:40:00+00:00'),
(20, 2, 6, 'Semilla de tomate', 10.000, '2026-09-01 09:45:00+00:00');

-- ============================================================
-- PRECIOS
-- ============================================================
INSERT INTO precios_producto (id, administrador_id, producto_id, tipo_cliente, precio, moneda, vigente_desde, vigente_hasta, creado_en) VALUES
(1, 1, 1, 'individual', 50.00, 'BOB', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(2, 1, 2, 'individual', 30.00, 'BOB', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(3, 1, 3, 'individual', 1.50, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(4, 1, 4, 'individual', 80.00, 'BOB', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(5, 1, 5, 'individual', 450.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(6, 1, 6, 'individual', 220.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(7, 1, 7, 'individual', 120.00, 'BOB', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(8, 1, 8, 'individual', 130.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(9, 1, 9, 'individual', 15.00, 'BOB', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(10, 1, 10, 'individual', 25.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(11, 2, 11, 'individual', 2.50, 'USD', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(12, 2, 12, 'individual', 4.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(13, 2, 13, 'individual', 3.50, 'USD', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(14, 2, 14, 'individual', 6.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(15, 2, 15, 'individual', 12.00, 'USD', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(16, 2, 16, 'individual', 1.20, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(17, 2, 17, 'individual', 8.00, 'USD', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(18, 2, 18, 'individual', 5.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(19, 2, 19, 'individual', 9.00, 'USD', '2026-11-01 00:00:00+00:00', NULL, '2026-11-01 00:00:00+00:00'),
(20, 2, 20, 'individual', 2.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(21, 1, 1, 'individual', 45.00, 'BOB', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(22, 1, 2, 'individual', 25.00, 'BOB', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(23, 1, 4, 'individual', 70.00, 'BOB', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(24, 1, 7, 'individual', 100.00, 'BOB', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(25, 1, 9, 'individual', 12.00, 'BOB', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(26, 2, 11, 'individual', 2.00, 'USD', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(27, 2, 13, 'individual', 3.00, 'USD', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(28, 2, 15, 'individual', 10.00, 'USD', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(29, 2, 17, 'individual', 7.00, 'USD', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(30, 2, 19, 'individual', 8.00, 'USD', '2026-08-01 00:00:00+00:00', '2026-11-01 00:00:00+00:00', '2026-08-01 00:00:00+00:00'),
(31, 1, 1, 'productor', 45.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(32, 1, 2, 'productor', 25.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(33, 1, 3, 'productor', 1.20, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(34, 2, 11, 'productor', 2.20, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(35, 2, 12, 'productor', 3.50, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(36, 2, 13, 'productor', 3.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(37, 1, 1, 'mayoreo', 40.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(38, 1, 2, 'mayoreo', 22.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(39, 1, 3, 'mayoreo', 1.00, 'BOB', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(40, 2, 11, 'mayoreo', 2.00, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(41, 2, 12, 'mayoreo', 3.20, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00'),
(42, 2, 13, 'mayoreo', 2.80, 'USD', '2026-09-01 00:00:00+00:00', NULL, '2026-09-01 00:00:00+00:00');

-- ============================================================
-- PROVEEDORES
-- ============================================================
INSERT INTO proveedores (id, administrador_id, nombre, contacto) VALUES
(1, 1, 'Proveedor Andino', 'Carlos Perez'),
(2, 1, 'Ferreteria Mayorista', 'Maria Lopez'),
(3, 2, 'ElectroSuministros', 'Jorge Ruiz'),
(4, 2, 'Jardin Verde', 'Lucia Gomez');

-- ============================================================
-- COMPRAS
-- ============================================================
INSERT INTO compras (id, administrador_id, proveedor_id, usuario_id, moneda, fecha, total, estado, nota) VALUES
(1, 1, 1, 1, 'BOB', '2026-11-02 09:00:00+00:00', 1400.00, 'confirmada', 'Reposicion de materiales'),
(2, 1, 2, 1, 'BOB', '2026-11-03 09:00:00+00:00', 1950.00, 'confirmada', 'Reposicion de herramientas y pintura'),
(3, 2, 3, 2, 'USD', '2026-11-04 09:00:00+00:00', 160.00, 'confirmada', 'Reposicion electrica'),
(4, 2, 4, 2, 'USD', '2026-11-05 09:00:00+00:00', 95.00, 'confirmada', 'Reposicion de jardin');

INSERT INTO compra_detalle (id, compra_id, administrador_id, producto_id, cantidad, costo_unitario, subtotal) VALUES
(1, 1, 1, 1, 20.000, 40.00, 800.00),
(2, 1, 1, 2, 30.000, 20.00, 600.00),
(3, 2, 1, 4, 10.000, 60.00, 600.00),
(4, 2, 1, 7, 15.000, 90.00, 1350.00),
(5, 3, 2, 11, 50.000, 2.00, 100.00),
(6, 3, 2, 12, 20.000, 3.00, 60.00),
(7, 4, 2, 17, 10.000, 6.00, 60.00),
(8, 4, 2, 19, 5.000, 7.00, 35.00);

-- ============================================================
-- VENTAS
-- ============================================================
INSERT INTO ventas (id, administrador_id, vendedor_id, cliente_nombre, tipo_cliente, canal_venta, moneda, fecha, total, estado, nota) VALUES
(1, 1, 3, 'Cliente Mostrador', 'individual', 'whatsapp', 'BOB', '2026-11-10 15:00:00+00:00', 180.00, 'confirmada', 'Venta de materiales'),
(2, 1, 3, 'Constructora Sur', 'individual', 'instagram', 'BOB', '2026-11-11 15:00:00+00:00', 435.00, 'confirmada', 'Pedido de pintura'),
(3, 1, 4, 'Cliente Final', 'individual', 'presencial', 'BOB', '2026-11-12 15:00:00+00:00', 135.00, 'confirmada', 'Venta mostrador'),
(4, 2, 7, 'Electricista Pro', 'individual', 'whatsapp', 'USD', '2026-11-13 15:00:00+00:00', 17.00, 'confirmada', 'Instalacion electrica'),
(5, 2, 7, 'Vecino', 'individual', 'presencial', 'USD', '2026-11-14 15:00:00+00:00', 42.00, 'confirmada', 'Venta de jardin'),
(6, 2, 8, 'Jardin Norte', 'individual', 'facebook', 'USD', '2026-11-15 15:00:00+00:00', 11.00, 'confirmada', 'Venta de electricidad');

INSERT INTO venta_detalle (id, venta_id, administrador_id, producto_id, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 1, 1, 2.000, 50.00, 100.00),
(2, 1, 1, 4, 1.000, 80.00, 80.00),
(3, 2, 1, 7, 3.000, 120.00, 360.00),
(4, 2, 1, 9, 5.000, 15.00, 75.00),
(5, 3, 1, 2, 4.000, 30.00, 120.00),
(6, 3, 1, 3, 10.000, 1.50, 15.00),
(7, 4, 2, 11, 2.000, 2.50, 5.00),
(8, 4, 2, 15, 1.000, 12.00, 12.00),
(9, 5, 2, 17, 3.000, 8.00, 24.00),
(10, 5, 2, 19, 2.000, 9.00, 18.00),
(11, 6, 2, 12, 1.000, 4.00, 4.00),
(12, 6, 2, 13, 2.000, 3.50, 7.00);

-- ============================================================
-- MOVIMIENTOS DE INVENTARIO
-- ============================================================
INSERT INTO movimiento_inventario (id, administrador_id, producto_id, motivo, cantidad, fecha, costo_unitario, precio_unitario, referencia_tipo, referencia_id, usuario_id, nota) VALUES
(1, 1, 1, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(2, 1, 2, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(3, 1, 3, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(4, 1, 4, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(5, 1, 5, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(6, 1, 6, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(7, 1, 7, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(8, 1, 8, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(9, 1, 9, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(10, 1, 10, 'ajuste_pos', 50.000, '2026-09-01 08:30:00+00:00', NULL, NULL, NULL, NULL, 1, 'Stock inicial'),
(11, 2, 11, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(12, 2, 12, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(13, 2, 13, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(14, 2, 14, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(15, 2, 15, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(16, 2, 16, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(17, 2, 17, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(18, 2, 18, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(19, 2, 19, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(20, 2, 20, 'ajuste_pos', 50.000, '2026-09-01 09:00:00+00:00', NULL, NULL, NULL, NULL, 2, 'Stock inicial'),
(21, 1, 1, 'compra', 20.000, '2026-11-02 09:00:00+00:00', 40.00, NULL, 'compra', 1, 1, 'Reposicion de materiales'),
(22, 1, 2, 'compra', 30.000, '2026-11-02 09:00:00+00:00', 20.00, NULL, 'compra', 1, 1, 'Reposicion de materiales'),
(23, 1, 4, 'compra', 10.000, '2026-11-03 09:00:00+00:00', 60.00, NULL, 'compra', 2, 1, 'Reposicion de herramientas'),
(24, 1, 7, 'compra', 15.000, '2026-11-03 09:00:00+00:00', 90.00, NULL, 'compra', 2, 1, 'Reposicion de pintura'),
(25, 2, 11, 'compra', 50.000, '2026-11-04 09:00:00+00:00', 2.00, NULL, 'compra', 3, 2, 'Reposicion electrica'),
(26, 2, 12, 'compra', 20.000, '2026-11-04 09:00:00+00:00', 3.00, NULL, 'compra', 3, 2, 'Reposicion electrica'),
(27, 2, 17, 'compra', 10.000, '2026-11-05 09:00:00+00:00', 6.00, NULL, 'compra', 4, 2, 'Reposicion de jardin'),
(28, 2, 19, 'compra', 5.000, '2026-11-05 09:00:00+00:00', 7.00, NULL, 'compra', 4, 2, 'Reposicion de jardin'),
(29, 1, 1, 'venta', 2.000, '2026-11-10 15:00:00+00:00', NULL, 50.00, 'venta', 1, 3, 'Venta de materiales'),
(30, 1, 4, 'venta', 1.000, '2026-11-10 15:00:00+00:00', NULL, 80.00, 'venta', 1, 3, 'Venta de materiales'),
(31, 1, 7, 'venta', 3.000, '2026-11-11 15:00:00+00:00', NULL, 120.00, 'venta', 2, 3, 'Pedido de pintura'),
(32, 1, 9, 'venta', 5.000, '2026-11-11 15:00:00+00:00', NULL, 15.00, 'venta', 2, 3, 'Pedido de pintura'),
(33, 1, 2, 'venta', 4.000, '2026-11-12 15:00:00+00:00', NULL, 30.00, 'venta', 3, 4, 'Venta mostrador'),
(34, 1, 3, 'venta', 10.000, '2026-11-12 15:00:00+00:00', NULL, 1.50, 'venta', 3, 4, 'Venta mostrador'),
(35, 2, 11, 'venta', 2.000, '2026-11-13 15:00:00+00:00', NULL, 2.50, 'venta', 4, 7, 'Instalacion electrica'),
(36, 2, 15, 'venta', 1.000, '2026-11-13 15:00:00+00:00', NULL, 12.00, 'venta', 4, 7, 'Instalacion electrica'),
(37, 2, 17, 'venta', 3.000, '2026-11-14 15:00:00+00:00', NULL, 8.00, 'venta', 5, 7, 'Venta de jardin'),
(38, 2, 19, 'venta', 2.000, '2026-11-14 15:00:00+00:00', NULL, 9.00, 'venta', 5, 7, 'Venta de jardin'),
(39, 2, 12, 'venta', 1.000, '2026-11-15 15:00:00+00:00', NULL, 4.00, 'venta', 6, 8, 'Venta de electricidad'),
(40, 2, 13, 'venta', 2.000, '2026-11-15 15:00:00+00:00', NULL, 3.50, 'venta', 6, 8, 'Venta de electricidad'),
(41, 1, 3, 'merma', 2.000, '2026-11-16 10:00:00+00:00', NULL, NULL, NULL, NULL, 1, 'Rotura de mercaderia'),
(42, 1, 5, 'ajuste_neg', 1.000, '2026-11-16 10:05:00+00:00', NULL, NULL, NULL, NULL, 1, 'Ajuste de inventario'),
(43, 2, 13, 'merma', 1.000, '2026-11-16 10:10:00+00:00', NULL, NULL, NULL, NULL, 2, 'Lampara dañada'),
(44, 2, 15, 'devolucion', 1.000, '2026-11-17 10:00:00+00:00', NULL, 12.00, 'venta', 4, 2, 'Devolucion de cliente');

-- ============================================================
-- PAGOS
-- ============================================================
INSERT INTO pagos (id, administrador_id, venta_id, metodo, monto, moneda, fecha) VALUES
(1, 1, 1, 'efectivo', 100.00, 'BOB', '2026-11-10 15:05:00+00:00'),
(2, 1, 2, 'transferencia', 435.00, 'BOB', '2026-11-11 15:10:00+00:00'),
(3, 2, 4, 'qr', 17.00, 'USD', '2026-11-13 15:05:00+00:00'),
(4, 2, 5, 'tarjeta', 20.00, 'USD', '2026-11-14 15:10:00+00:00');
