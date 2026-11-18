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
- `apps`: adaptadores Django. Los modelos son `managed = True`: las migraciones
  crean las tablas y las restricciones básicas. El esquema SQL de PostgreSQL
  agrega las claves compuestas, los triggers y las restricciones adicionales.

## Base de datos

### PostgreSQL (recomendado)

El esquema completo está en `infrastructure/sql/001_schema.sql`. Está pensado
para PostgreSQL e incluye claves compuestas, índices parciales, `TIMESTAMPTZ`,
triggers y restricciones de moneda.

```bash
createdb sistema_taller
psql -d sistema_taller -v ON_ERROR_STOP=1 -f infrastructure/sql/001_schema.sql
```

Después se marcan como aplicadas las migraciones iniciales del negocio y se
crean las tablas propias de Django (sesiones y admin):

```bash
python manage.py migrate --fake-initial
```

Ese camino conserva los triggers, las claves compuestas y los checks del SQL.
Si se ejecuta `migrate` normal sobre una base PostgreSQL vacía, Django crea las
tablas, pero **no** crea esos triggers ni las claves compuestas.

Variables de entorno (podés copiar `.env.example`):

```
POSTGRES_DB=sistema_taller
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=una_clave_segura
```

### SQLite (desarrollo rápido)

Sin `POSTGRES_DB`, Django usa SQLite. El proyecto prepara automáticamente las
tablas del negocio y triggers de desarrollo:

```bash
python manage.py dev_setup
```

o simplemente:

```bash
python manage.py runserver
```

Con `DEBUG=True` y SQLite, el comando `runserver` ejecuta `migrate` y crea el
esquema de desarrollo antes de arrancar. En PostgreSQL no se auto-migra: hay que
aplicar el SQL y ejecutar `migrate`.

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
- `POST /api/inventario/ventas/<id>/anular/`
- `POST /api/inventario/compras/<id>/anular/`
- `GET|POST /api/inventario/pagos/`
- `GET|PATCH /api/usuarios/admin/perfil/`

Los endpoints de escritura usan los casos de uso. En PostgreSQL los triggers
generan los movimientos de inventario al confirmar ventas y compras; en SQLite
esos triggers también se crean en el esquema de desarrollo. La moneda del
administrador se usa para nuevas tarifas y se conserva por venta, compra y pago.

## Datos de demostración

Con las tablas creadas y la base sin datos de negocio:

```bash
python manage.py seed_demo
```

Eso carga `infrastructure/seed/seed_demo.sql` y ajusta las secuencias. Incluye:

- 2 administradores y 6 vendedores.
- 6 categorías y 20 productos (10 por administrador).
- 42 precios, incluyendo cambios de precio históricos y tarifas de productor/mayoreo.
- 4 proveedores, 4 compras, 6 ventas, 44 movimientos de inventario y 4 pagos.

Usuarios de prueba:

```
admin1@taller.com
admin2@taller.com
vendedor1@taller.com ... vendedor6@taller.com
Contraseña: Password123!
```

También se puede cargar el SQL directo:

```bash
sqlite3 db.sqlite3 < infrastructure/seed/seed_demo.sql
```

En PostgreSQL, después del SQL directo ejecutar
`infrastructure/seed/reset_sequences_postgres.sql`.

## Pruebas

Pruebas de dominio (no requieren base de datos):

```bash
python -m unittest discover -s tests -t .
```

o

```bash
pytest
```

Para probar los endpoints alcanza con SQLite (`python manage.py dev_setup` o
`runserver`). Para PostgreSQL, aplicar `infrastructure/sql/001_schema.sql` y
luego `python manage.py migrate --fake-initial`.

## Nota de seguridad

Las vistas DRF son `csrf_exempt` y la autenticación es por sesión, porque el
JavaScript existente no envía token CSRF. Antes de exponer el sistema en
producción hay que agregar CSRF o adaptar el front-end. Ver `docs/DECISIONES.md`.
