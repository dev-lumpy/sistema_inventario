# SistemaTaller

Reconstrucción del backend sobre arquitectura hexagonal. El front-end existente
(`templates/` y `static/`) se conserva tal cual.

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
    ports/                Interfaces de repositorios y UnitOfWork

apps/                     Infraestructura Django
  accounts/               Modelos ORM unmanaged
  catalog/
  sales/
  purchases/
  payments/
  pages/                  Vistas que sirven el front-end

infrastructure/sql/       Esquema PostgreSQL canónico
config/                   Configuración Django
```

## Capas

- `core/domain`: entidades, value objects, reglas e invariantes. No importa Django.
- `core/application/ports`: contratos que la infraestructura debe implementar.
- `apps`: adaptadores Django. Los modelos están declarados con `managed = False`
  porque las tablas las crea el esquema SQL, no las migraciones de Django.

## Base de datos

El esquema completo está en `infrastructure/sql/001_schema.sql`. Está pensado
para PostgreSQL e incluye claves compuestas, índices parciales y triggers.

```bash
createdb sistema_taller
psql -d sistema_taller -f infrastructure/sql/001_schema.sql
```

Variables de entorno para conectar Django a PostgreSQL:

```
POSTGRES_DB=sistema_taller
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=una_clave_segura
```

Sin `POSTGRES_DB`, Django usa SQLite solo para desarrollo del front-end.

## Desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

Las rutas del front-end quedan en `/`, `/login/`, `/register/` y `/dashboard/`.
La autenticación y las APIs REST todavía no están implementadas; los endpoints
que consume el JavaScript se reconstruirán como adaptadores de los puertos.

## Pruebas

```bash
python -m unittest discover -s tests
```

o

```bash
pytest
```
