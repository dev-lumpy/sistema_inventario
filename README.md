# SistemaTaller

Backend reconstruido sobre arquitectura hexagonal. El front-end existente
(`templates/` y `static/`) se conserva sin cambios.

Las decisiones de diseño están documentadas en `docs/DECISIONES.md`.

## Estructura

```
core/
  domain/                 Reglas de negocio puras (sin Django)
    shared/               Money, Quantity, errores, enums compartidos
    accounts/             Usuario, Administrador, Vendedor, Vinculo
    catalog/              Categoria, Producto, PrecioProducto, MovimientoInventario
    sales/                Venta, VentaDetalle
    purchases/            Proveedor, Compra, CompraDetalle
    payments/             Pago
  application/
    ports/                Interfaces de repositorios, PasswordHasher y UnitOfWork
    accounts/             Casos de uso de registro, login y vínculos
    catalog/              Casos de uso de catálogo y movimientos
    payments/             Casos de uso de pagos

apps/                     Infraestructura Django
  accounts/               Modelos ORM, repositorios, auth y endpoints
  catalog/                Modelos ORM, repositorios, queries y endpoints
  sales/                  Modelos ORM y repositorio
  purchases/              Modelos ORM y repositorio
  payments/               Modelos ORM y repositorio
  pages/                  Vistas que sirven el front-end
  common/                 Manejo común de errores HTTP

infrastructure/sql/       Esquema PostgreSQL canónico
config/                   Configuración Django
```

## Capas

- `core/domain`: entidades, value objects, reglas e invariantes. No importa Django.
- `core/application`: puertos y casos de uso. Recibe las dependencias por
  inyección.
- `apps`: adaptadores Django. Los modelos están declarados con `managed = False`
  porque las tablas las crea el esquema SQL, no las migraciones de Django.

## Base de datos

El esquema completo está en `infrastructure/sql/001_schema.sql`. Está pensado
para PostgreSQL e incluye claves compuestas, índices parciales, `TIMESTAMPTZ` y
triggers.

```bash
createdb sistema_taller
psql -d sistema_taller -v ON_ERROR_STOP=1 -f infrastructure/sql/001_schema.sql
```

Después se crean las tablas propias de Django (sesiones y admin):

```bash
python manage.py migrate
```

Variables de entorno (podés copiar `.env.example`):

```
POSTGRES_DB=sistema_taller
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=una_clave_segura
```

Sin `POSTGRES_DB`, Django usa SQLite solo para desarrollo del front-end. Las
tablas del negocio no existen en SQLite porque las crea el SQL de PostgreSQL.

## Desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py check
python manage.py runserver
```

Rutas del front-end: `/`, `/login/`, `/register/` y `/dashboard/`.

## Autenticación y API

La autenticación usa sesiones de Django y cookies. El login guarda
`usuario_id`, `rol` y `nombre` en la sesión. No se usa JWT.

Endpoints principales:

- `POST /api/usuarios/auth/login/`
- `POST /api/usuarios/auth/logout/`
- `POST /api/usuarios/registrar-admin/`
- `POST /api/usuarios/registrar-vendedor/`
- `GET /api/usuarios/get_user/admin/<id>/vendedores/`
- `PATCH|DELETE /api/usuarios/api/<id>/`
- `GET|POST /api/usuarios/solicitudes-admin/`
- `GET|POST /api/inventario/productos/`
- `GET /api/inventario/productos/select_all/`
- `GET /api/inventario/productos/alertas/`
- `GET|POST /api/inventario/add_categoria/`
- `GET|POST /api/inventario/proveedores/select/`
- `GET /api/inventario/resumen/hoy/`
- `GET /api/inventario/resumen/periodo/`
- `POST /api/inventario/movimiento/entrada/`
- `POST /api/inventario/movimiento/salida/`
- `GET /api/inventario/movimiento/entrada/historial/`
- `GET /api/inventario/history_movimientos/<limite>/`
- `GET /api/inventario/reportes/pdf/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`

Los endpoints de escritura usan los casos de uso y los triggers de PostgreSQL
generan los movimientos de inventario al confirmar ventas y compras.

## Pruebas

Pruebas de dominio (no requieren base de datos):

```bash
python -m unittest discover -s tests -t .
```

o

```bash
pytest
```

Para probar los endpoints hace falta PostgreSQL con
`infrastructure/sql/001_schema.sql` aplicado.

## Nota de seguridad

Las vistas DRF son `csrf_exempt` y la autenticación es por sesión, porque el
JavaScript existente no envía token CSRF. Antes de exponer el sistema en
producción hay que agregar CSRF o adaptar el front-end. Ver `docs/DECISIONES.md`.
