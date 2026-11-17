-- ============================================================
-- 0. EXTENSIONES
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- 1. USUARIOS
-- ============================================================
CREATE TABLE usuarios (
    id                    SERIAL PRIMARY KEY,
    nombre                VARCHAR(100) NOT NULL,
    apellidos             VARCHAR(100),
    user_name             VARCHAR(50)  UNIQUE NOT NULL,
    correo                VARCHAR(150) UNIQUE NOT NULL,
    password_hash         TEXT NOT NULL,
    debe_cambiar_password BOOLEAN NOT NULL DEFAULT true,
    activo                BOOLEAN NOT NULL DEFAULT true,
    creado_en             TIMESTAMP NOT NULL DEFAULT now()
);


-- ============================================================
-- 2. ADMINISTRADORES (subtipo de usuarios, PK = FK)
-- ============================================================
CREATE TABLE administradores (
    id             INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre_negocio VARCHAR(150)
);


-- ============================================================
-- 3. VENDEDORES (subtipo de usuarios, PK = FK)
-- ============================================================
CREATE TABLE vendedores (
    id               INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    creado_por_admin INT REFERENCES administradores(id),
    creado_en        TIMESTAMP NOT NULL DEFAULT now(),
    bloqueado        BOOLEAN NOT NULL DEFAULT false,
    motivo_bloqueo   TEXT,
    bloqueado_en     TIMESTAMP
);


-- ============================================================
-- 4. VINCULO VENDEDOR <-> ADMINISTRADOR (N:M con estado)
-- ============================================================
CREATE TABLE vendedor_administrador (
    vendedor_id      INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    estado           VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    solicitado_por   VARCHAR(20) NOT NULL,
    motivo_estado    TEXT,
    creado_en        TIMESTAMP NOT NULL DEFAULT now(),
    actualizado_en   TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (vendedor_id, administrador_id),
    CONSTRAINT chk_va_estado
        CHECK (estado IN ('pendiente','aceptado','rechazado','inactivo')),
    CONSTRAINT chk_va_solicitado
        CHECK (solicitado_por IN ('admin','vendedor'))
);


-- ============================================================
-- 5. CATEGORIAS (por tenant)
-- ============================================================
CREATE TABLE categorias (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    nombre           VARCHAR(100) NOT NULL,
    CONSTRAINT uq_categoria_admin UNIQUE (id, administrador_id),
    CONSTRAINT uq_categoria_nombre UNIQUE (administrador_id, nombre)
);


-- ============================================================
-- 6. PRODUCTOS (por tenant)
-- ============================================================
CREATE TABLE productos (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    categoria_id     INT NOT NULL,
    nombre           VARCHAR(200) NOT NULL,
    creado_en        TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_producto_admin UNIQUE (id, administrador_id),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (categoria_id, administrador_id)
        REFERENCES categorias (id, administrador_id)
);


-- ============================================================
-- 7. PRECIOS_PRODUCTO (historial de vigencias, por tenant)
-- ============================================================
CREATE TABLE precios_producto (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    producto_id      INT NOT NULL,
    tipo_cliente     VARCHAR(20) NOT NULL,
    precio           NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    moneda           CHAR(3) NOT NULL DEFAULT 'BOB',
    vigente_desde    TIMESTAMP NOT NULL DEFAULT now(),
    vigente_hasta    TIMESTAMP,
    creado_en        TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_precio_producto
        FOREIGN KEY (producto_id, administrador_id)
        REFERENCES productos (id, administrador_id),
    CONSTRAINT chk_precio_tipo_cliente
        CHECK (tipo_cliente IN ('individual','productor','mayoreo')),
    CONSTRAINT chk_precio_vigencia
        CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde)
);
CREATE UNIQUE INDEX uq_precio_vigente
    ON precios_producto (producto_id, tipo_cliente)
    WHERE vigente_hasta IS NULL;


-- ============================================================
-- 8. VENTAS (cabecera, por tenant)
-- ============================================================
CREATE TABLE ventas (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    vendedor_id      INT NOT NULL REFERENCES vendedores(id),
    cliente_nombre   VARCHAR(150),
    tipo_cliente     VARCHAR(20) NOT NULL,
    fecha            TIMESTAMP NOT NULL DEFAULT now(),
    total            NUMERIC(12,2) NOT NULL DEFAULT 0,
    estado           VARCHAR(20) NOT NULL DEFAULT 'borrador',
    nota             TEXT,
    CONSTRAINT uq_venta_admin UNIQUE (id, administrador_id),
    CONSTRAINT chk_venta_tipo_cliente
        CHECK (tipo_cliente IN ('individual','productor','mayoreo')),
    CONSTRAINT chk_venta_estado
        CHECK (estado IN ('borrador','confirmada','anulada')),
    CONSTRAINT chk_venta_total CHECK (total >= 0)
);


-- ============================================================
-- 9. VENTA_DETALLE (líneas; protegida por FK compuesta)
-- ============================================================
CREATE TABLE venta_detalle (
    id               SERIAL PRIMARY KEY,
    venta_id         INT NOT NULL,
    administrador_id INT NOT NULL,
    producto_id      INT NOT NULL,
    cantidad         NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    precio_unitario  NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal         NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT fk_detalle_venta
        FOREIGN KEY (venta_id, administrador_id)
        REFERENCES ventas (id, administrador_id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (producto_id, administrador_id)
        REFERENCES productos (id, administrador_id)
);


-- ============================================================
-- 10. PROVEEDORES (por tenant)
-- ============================================================
CREATE TABLE proveedores (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    nombre           VARCHAR(150) NOT NULL,
    contacto         VARCHAR(150),
    CONSTRAINT uq_proveedor_admin UNIQUE (id, administrador_id)
);


-- ============================================================
-- 11. COMPRAS (cabecera, por tenant)
-- ============================================================
CREATE TABLE compras (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    proveedor_id     INT NOT NULL,
    fecha            TIMESTAMP NOT NULL DEFAULT now(),
    total            NUMERIC(12,2) NOT NULL DEFAULT 0,
    estado           VARCHAR(20) NOT NULL DEFAULT 'borrador',
    nota             TEXT,
    CONSTRAINT uq_compra_admin UNIQUE (id, administrador_id),
    CONSTRAINT fk_compra_proveedor
        FOREIGN KEY (proveedor_id, administrador_id)
        REFERENCES proveedores (id, administrador_id),
    CONSTRAINT chk_compra_estado
        CHECK (estado IN ('borrador','confirmada','anulada')),
    CONSTRAINT chk_compra_total CHECK (total >= 0)
);


-- ============================================================
-- 12. COMPRA_DETALLE (protegida por FK compuesta)
-- ============================================================
CREATE TABLE compra_detalle (
    id              SERIAL PRIMARY KEY,
    compra_id       INT NOT NULL,
    administrador_id INT NOT NULL,
    producto_id     INT NOT NULL,
    cantidad        NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    costo_unitario  NUMERIC(12,2) NOT NULL CHECK (costo_unitario >= 0),
    subtotal        NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT fk_cdetalle_compra
        FOREIGN KEY (compra_id, administrador_id)
        REFERENCES compras (id, administrador_id) ON DELETE CASCADE,
    CONSTRAINT fk_cdetalle_producto
        FOREIGN KEY (producto_id, administrador_id)
        REFERENCES productos (id, administrador_id)
);


-- ============================================================
-- 13. MOVIMIENTO_INVENTARIO (kardex, por tenant)
-- ============================================================
CREATE TABLE movimiento_inventario (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    producto_id      INT NOT NULL,
    motivo           VARCHAR(30) NOT NULL,
    cantidad         NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    fecha            TIMESTAMP NOT NULL DEFAULT now(),
    costo_unitario   NUMERIC(12,2) CHECK (costo_unitario IS NULL OR costo_unitario >= 0),
    precio_unitario  NUMERIC(12,2) CHECK (precio_unitario IS NULL OR precio_unitario >= 0),
    referencia_tipo  VARCHAR(20),
    referencia_id    INT,
    usuario_id       INT NOT NULL REFERENCES usuarios(id),
    nota             TEXT,
    CONSTRAINT fk_mov_producto
        FOREIGN KEY (producto_id, administrador_id)
        REFERENCES productos (id, administrador_id),
    CONSTRAINT chk_mov_motivo
        CHECK (motivo IN ('compra','venta','devolucion','merma','ajuste_pos','ajuste_neg')),
    CONSTRAINT chk_mov_referencia
        CHECK ((referencia_tipo IS NULL AND referencia_id IS NULL)
            OR (referencia_tipo IS NOT NULL AND referencia_id IS NOT NULL)),
    CONSTRAINT chk_mov_ref_tipo
        CHECK (referencia_tipo IS NULL
            OR referencia_tipo IN ('venta','compra','ajuste'))
);


-- ============================================================
-- 14. PAGOS (por venta)
-- ============================================================
CREATE TABLE pagos (
    id               SERIAL PRIMARY KEY,
    administrador_id INT NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    venta_id         INT NOT NULL,
    metodo           VARCHAR(30) NOT NULL,
    monto            NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    fecha            TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_pago_venta
        FOREIGN KEY (venta_id, administrador_id)
        REFERENCES ventas (id, administrador_id) ON DELETE CASCADE,
    CONSTRAINT chk_pago_metodo
        CHECK (metodo IN ('efectivo','transferencia','qr','tarjeta','otro'))
);


-- ============================================================
-- INDICES
-- ============================================================
CREATE INDEX idx_productos_admin            ON productos (administrador_id);
CREATE INDEX idx_categorias_admin           ON categorias (administrador_id);
CREATE INDEX idx_precios_producto           ON precios_producto (producto_id, tipo_cliente);
CREATE INDEX idx_ventas_admin_fecha         ON ventas (administrador_id, fecha);
CREATE INDEX idx_ventas_vendedor            ON ventas (vendedor_id);
CREATE INDEX idx_venta_detalle_venta        ON venta_detalle (venta_id);
CREATE INDEX idx_venta_detalle_producto     ON venta_detalle (producto_id);
CREATE INDEX idx_compras_admin_fecha        ON compras (administrador_id, fecha);
CREATE INDEX idx_compra_detalle_compra      ON compra_detalle (compra_id);
CREATE INDEX idx_mov_admin_producto_fecha   ON movimiento_inventario (administrador_id, producto_id, fecha);
CREATE INDEX idx_mov_referencia             ON movimiento_inventario (referencia_tipo, referencia_id);
CREATE INDEX idx_va_admin_estado            ON vendedor_administrador (administrador_id, estado);
CREATE INDEX idx_pagos_venta                ON pagos (venta_id);


-- ============================================================
-- TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION fn_validar_vinculo_venta() RETURNS TRIGGER AS $$
DECLARE
    v_estado VARCHAR(20);
    v_bloqueado BOOLEAN;
BEGIN
    SELECT va.estado, v.bloqueado INTO v_estado, v_bloqueado
    FROM vendedor_administrador va
    JOIN vendedores v ON v.id = va.vendedor_id
    WHERE va.vendedor_id = NEW.vendedor_id
      AND va.administrador_id = NEW.administrador_id;

    IF v_estado IS NULL THEN
        RAISE EXCEPTION 'El vendedor % no tiene vínculo con el admin %',
            NEW.vendedor_id, NEW.administrador_id;
    END IF;
    IF v_estado <> 'aceptado' THEN
        RAISE EXCEPTION 'El vínculo vendedor % / admin % está en estado %, no puede vender',
            NEW.vendedor_id, NEW.administrador_id, v_estado;
    END IF;
    IF v_bloqueado THEN
        RAISE EXCEPTION 'El vendedor % está bloqueado a nivel plataforma', NEW.vendedor_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_vinculo_venta
BEFORE INSERT OR UPDATE OF vendedor_id, administrador_id ON ventas
FOR EACH ROW EXECUTE FUNCTION fn_validar_vinculo_venta();


CREATE OR REPLACE FUNCTION fn_validar_precio_linea() RETURNS TRIGGER AS $$
DECLARE
    v_admin_venta INT;
    v_tipo_cliente VARCHAR(20);
    v_existe INT;
BEGIN
    SELECT administrador_id, tipo_cliente INTO v_admin_venta, v_tipo_cliente
    FROM ventas WHERE id = NEW.venta_id;

    SELECT 1 INTO v_existe
    FROM precios_producto
    WHERE producto_id = NEW.producto_id
      AND administrador_id = v_admin_venta
      AND tipo_cliente = v_tipo_cliente
      AND vigente_hasta IS NULL;

    IF v_existe IS NULL THEN
        RAISE EXCEPTION 'No hay tarifa vigente para producto % / tipo %',
            NEW.producto_id, v_tipo_cliente;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_precio_linea
BEFORE INSERT OR UPDATE ON venta_detalle
FOR EACH ROW EXECUTE FUNCTION fn_validar_precio_linea();


CREATE OR REPLACE FUNCTION fn_validar_stock_venta() RETURNS TRIGGER AS $$
DECLARE
    v_estado VARCHAR(20);
    v_stock NUMERIC(14,3);
BEGIN
    SELECT estado INTO v_estado FROM ventas WHERE id = NEW.venta_id;
    IF v_estado <> 'confirmada' THEN
        RETURN NEW;
    END IF;

    SELECT COALESCE(SUM(
        CASE WHEN motivo IN ('compra','devolucion','ajuste_pos') THEN cantidad
             WHEN motivo IN ('venta','merma','ajuste_neg')       THEN -cantidad
        END), 0) INTO v_stock
    FROM movimiento_inventario
    WHERE administrador_id = NEW.administrador_id
      AND producto_id = NEW.producto_id;

    IF v_stock < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente del producto %: hay %, se intenta vender %',
            NEW.producto_id, v_stock, NEW.cantidad;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_stock_venta
BEFORE INSERT ON venta_detalle
FOR EACH ROW EXECUTE FUNCTION fn_validar_stock_venta();


CREATE OR REPLACE FUNCTION fn_generar_movimiento_venta() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'confirmada' AND (OLD.estado IS DISTINCT FROM 'confirmada') THEN
        INSERT INTO movimiento_inventario
            (administrador_id, producto_id, motivo, cantidad,
             precio_unitario, referencia_tipo, referencia_id, usuario_id)
        SELECT vd.administrador_id, vd.producto_id, 'venta', vd.cantidad,
               vd.precio_unitario, 'venta', NEW.id, NEW.vendedor_id
        FROM venta_detalle vd
        WHERE vd.venta_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generar_movimiento_venta
AFTER UPDATE OF estado ON ventas
FOR EACH ROW EXECUTE FUNCTION fn_generar_movimiento_venta();


CREATE OR REPLACE FUNCTION fn_generar_movimiento_compra() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'confirmada' AND (OLD.estado IS DISTINCT FROM 'confirmada') THEN
        INSERT INTO movimiento_inventario
            (administrador_id, producto_id, motivo, cantidad,
             costo_unitario, referencia_tipo, referencia_id, usuario_id)
        SELECT cd.administrador_id, cd.producto_id, 'compra', cd.cantidad,
               cd.costo_unitario, 'compra', NEW.id,
               (SELECT u.id FROM usuarios u LIMIT 1)
        FROM compra_detalle cd
        WHERE cd.compra_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generar_movimiento_compra
AFTER UPDATE OF estado ON compras
FOR EACH ROW EXECUTE FUNCTION fn_generar_movimiento_compra();


CREATE OR REPLACE FUNCTION fn_recalcular_total_venta() RETURNS TRIGGER AS $$
BEGIN
    UPDATE ventas v
    SET total = COALESCE((
        SELECT SUM(subtotal) FROM venta_detalle
        WHERE venta_id = COALESCE(NEW.venta_id, OLD.venta_id)
    ), 0)
    WHERE v.id = COALESCE(NEW.venta_id, OLD.venta_id);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_recalcular_total_venta
AFTER INSERT OR UPDATE OR DELETE ON venta_detalle
FOR EACH ROW EXECUTE FUNCTION fn_recalcular_total_venta();


CREATE OR REPLACE FUNCTION fn_recalcular_total_compra() RETURNS TRIGGER AS $$
BEGIN
    UPDATE compras c
    SET total = COALESCE((
        SELECT SUM(subtotal) FROM compra_detalle
        WHERE compra_id = COALESCE(NEW.compra_id, OLD.compra_id)
    ), 0)
    WHERE c.id = COALESCE(NEW.compra_id, OLD.compra_id);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_recalcular_total_compra
AFTER INSERT OR UPDATE OR DELETE ON compra_detalle
FOR EACH ROW EXECUTE FUNCTION fn_recalcular_total_compra();


CREATE OR REPLACE FUNCTION fn_no_borrar_confirmada() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.estado = 'confirmada' THEN
        RAISE EXCEPTION 'No se puede borrar una venta confirmada (id %). Anúlala.', OLD.id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_no_borrar_venta_confirmada
BEFORE DELETE ON ventas
FOR EACH ROW EXECUTE FUNCTION fn_no_borrar_confirmada();


CREATE OR REPLACE FUNCTION fn_actualizar_timestamp_vinculo() RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_actualizar_timestamp_vinculo
BEFORE UPDATE ON vendedor_administrador
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp_vinculo();
