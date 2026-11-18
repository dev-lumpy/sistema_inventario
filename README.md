# SistemaTaller

Sistema de inventario y ventas para talleres, desarrollado con Django y Django
REST Framework. Permite administrar usuarios, categorías, productos, proveedores,
compras, movimientos de stock, ventas, pagos y reportes; cuenta con interfaces
separadas para administradores y vendedores.

El frontend existente se encuentra en `templates/` y `static/`. El backend fue
reconstruido siguiendo una arquitectura hexagonal y conserva el contrato HTTP
que consume ese frontend.

Las decisiones técnicas, sus alternativas y sus consecuencias se documentan en
[`docs/DECISIONES.md`](docs/DECISIONES.md).

## Contenido

- [Funcionalidades](#funcionalidades)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración](#configuración)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Bases de datos](#bases-de-datos)
- [Datos de demostración](#datos-de-demostración)
- [Roles y permisos](#roles-y-permisos)
- [Rutas web](#rutas-web)
- [API HTTP](#api-http)
- [Inventario y moneda](#inventario-y-moneda)
- [Pruebas](#pruebas)
- [Comandos útiles](#comandos-útiles)
- [Seguridad](#seguridad)
- [Problemas frecuentes](#problemas-frecuentes)

## Funcionalidades

### Administradores

- Registro y autenticación.
- Gestión de perfil y moneda operativa.
- Gestión de vendedores y solicitudes de vinculación.
- Administración de categorías y productos.
- Registro de precios individuales y por productor/mayoreo.
- Administración de proveedores.
- Registro de compras y entradas de inventario.
- Registro y anulación de ventas.
- Registro de pagos asociados a ventas.
- Consulta de alertas de stock mínimo.
- Consulta de resumen diario y por período.
- Consulta de productos y movimientos históricos.
- Generación de reportes PDF por período.

### Vendedores

- Inicio de sesión.
- Visualización del dashboard y resumen disponible.
- Registro de ventas.
- Consulta de productos e inventario.
- Consulta y gestión de solicitudes de vinculación.
- Operación con la moneda definida por el administrador vinculado.

### Reglas compartidas

- El stock no se almacena como un campo único: se calcula desde los movimientos
  de inventario.
- Las compras, ventas y movimientos usan cantidades `Decimal`.
- Los montos usan `Decimal` y se redondean a dos decimales.
- Las compras y ventas confirmadas pueden anularse, pero no borrarse.
- La confirmación de una venta verifica que exista stock suficiente.
- La moneda se configura por administrador y se conserva en ventas, compras y
  pagos.

## Tecnologías

- Python 3
- Django 5.2
- Django REST Framework
- PostgreSQL  (entorno recomendado)
- SQLite (entorno de desarrollo rápido)
- WeasyPrint para reportes PDF
- Whitenoise para archivos estáticos
- Sentry SDK
- python-dotenv
- pytest y pytest-django
- HTML, CSS y JavaScript sin framework frontend

Dependencias exactas disponibles en `requirements.txt` y
`requirements-dev.txt`.

## Arquitectura

El proyecto está organizado en tres capas principales:

```text
core/domain
    │ Reglas de negocio puras, entidades, value objects y errores
    ▼
core/application
    │ Casos de uso y puertos (interfaces de repositorios y servicios)
    ▼
apps + infrastructure
    Adaptadores Django, ORM, HTTP, base de datos y servicios externos
```

### `core/domain`

Contiene el modelo de negocio independiente de Django:

- cuentas, usuarios, administradores y vendedores;
- categorías, productos, precios y movimientos;
- ventas y sus líneas;
- compras y sus líneas;
- proveedores y pagos;
- `Money`, `Quantity`, validadores y errores compartidos.

### `core/application`

Contiene los casos de uso y las interfaces necesarias para ejecutarlos:

- registro, autenticación y vinculación de vendedores;
- gestión de catálogo e inventario;
- pagos;
- puertos de repositorio;
- puerto de cifrado de contraseñas;
- unidad de trabajo.

Los casos de uso reciben sus dependencias mediante puertos. Los views no deben
contener las reglas de negocio ni manejar transacciones manualmente.

### `apps`

Contiene los adaptadores Django:

- modelos ORM y repositorios;
- autenticación y permisos;
- endpoints REST;
- vistas de las páginas HTML;
- manejo común de excepciones;
- comandos de administración.

### `infrastructure`

Contiene infraestructura compartida:

- `django/unit_of_work.py`: implementación de la unidad de trabajo con
  transacciones atómicas;
- `sql/001_schema.sql`: esquema PostgreSQL completo;
- `seed/`: datos de demostración y ajuste de secuencias.

## Estructura del proyecto

```text
sistema_inventario/
├── apps/
│   ├── accounts/          Usuarios, autenticación y vínculos
│   ├── catalog/           Categorías, productos, stock y reportes
│   ├── common/            Errores y comandos de administración
│   ├── pages/             Páginas HTML del frontend
│   ├── payments/          Pagos
│   ├── purchases/         Compras
│   └── sales/             Ventas
├── config/
│   ├── settings.py        Configuración Django y entorno
│   └── urls.py            Enrutador principal
├── core/
│   ├── application/       Casos de uso y puertos
│   └── domain/            Entidades y reglas puras
├── docs/
│   └── DECISIONES.md      Registro de decisiones de arquitectura
├── infrastructure/
│   ├── django/            Unidad de trabajo Django
│   ├── seed/              Datos y secuencias de demostración
│   └── sql/               Esquema PostgreSQL
├── static/                JavaScript, CSS, fuentes e iconos
├── templates/             Plantillas Django del frontend y PDF
├── tests/                 Pruebas de dominio
├── .env.example           Ejemplo de variables de entorno
├── manage.py              Punto de entrada administrativo
├── pytest.ini             Configuración de pytest
├── requirements.txt       Dependencias de ejecución
└── requirements-dev.txt   Dependencias de desarrollo y pruebas
```

## Requisitos

- Python 3.10 o posterior recomendado.
- `pip` y `venv`.
- PostgreSQL 14 o posterior para la configuración completa.
- SQLite 3 para desarrollo rápido; no requiere servidor externo.
- Para PDF: dependencias nativas requeridas por WeasyPrint.

En Windows, PowerShell puede necesitar habilitar scripts si se usa la activación
del entorno virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Configuración

Partiendo de la raíz del proyecto, crea el archivo de entorno:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Variables disponibles:

| Variable | Valor predeterminado | Uso |
|---|---|---|
| `SECRET_KEY` | clave insegura de desarrollo | Firma de sesiones y Django |
| `DEBUG` | `1` | Activa modo de desarrollo |
| `ALLOWED_HOSTS` | `*` | Hosts HTTP permitidos |
| `POSTGRES_DB` | vacío | Si existe, activa PostgreSQL |
| `POSTGRES_USER` | `postgres` | Usuario PostgreSQL |
| `POSTGRES_PASSWORD` | vacío | Contraseña PostgreSQL |
| `POSTGRES_HOST` | `localhost` | Servidor PostgreSQL |
| `POSTGRES_PORT` | `5432` | Puerto PostgreSQL |
| `SENTRY_DSN` | vacío | DSN opcional de Sentry |

Para usar SQLite, elimina `POSTGRES_DB` del `.env` o deja su valor vacío.
Para usar PostgreSQL, define todas las variables necesarias.

Ejemplo de `.env` con PostgreSQL:

```dotenv
SECRET_KEY=cambia-esta-clave-en-produccion
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=sistema_taller
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SENTRY_DSN=
```

No subas el archivo `.env` al repositorio.

## Instalación y ejecución

### Windows, Linux o macOS con SQLite

```bash
python -m venv .venv
```

Activa el entorno:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Configura SQLite quitando `POSTGRES_DB` del `.env` y prepara las tablas:

```bash
python manage.py dev_setup
python manage.py check
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

Con `DEBUG=1`, SQLite y el servidor `runserver`, Django ejecuta las migraciones
y prepara el esquema de desarrollo automáticamente. Aunque existe ese
comportamiento automático, `dev_setup` sigue siendo el comando explícito y
recomendado para inicializar o revisar el entorno.

### PostgreSQL

1. Crea la base de datos:

```sql
CREATE DATABASE sistema_taller;
```

2. Aplica el esquema completo:

```bash
psql -d sistema_taller -v ON_ERROR_STOP=1 -f infrastructure/sql/001_schema.sql
```

Desde Windows PowerShell, también puede ejecutarse con la ruta completa de
`psql` o desde un símbolo del sistema configurado con PostgreSQL.

3. Registra las tablas administradas por Django:

```bash
python manage.py migrate --fake-initial
python manage.py check
python manage.py runserver
```

El esquema SQL es necesario para conservar claves compuestas, índices parciales,
triggers y restricciones adicionales que Django no representa directamente.
No se recomienda crear primero una base PostgreSQL vacía solo con las
migraciones: funcionaría parcialmente, pero faltaría parte de la lógica de
base de datos.

## Bases de datos

### SQLite

Usado por defecto cuando no existe `POSTGRES_DB`.

- Archivo local: `db.sqlite3`.
- Comando de preparación: `python manage.py dev_setup`.
- Se crea automáticamente al ejecutar `runserver` con `DEBUG=1`.
- Incluye una adaptación del esquema y de los triggers para desarrollo.
- Es apropiado para pruebas locales, demostraciones y desarrollo rápido.

### PostgreSQL

Usado cuando `POSTGRES_DB` está definido.

- Esquema canónico: `infrastructure/sql/001_schema.sql`.
- Usa `TIMESTAMPTZ`, claves compuestas, índices parciales y restricciones.
- Los triggers validan y registran movimientos de inventario.
- Requiere aplicar el SQL antes de ejecutar las migraciones de Django.

## Datos de demostración

El comando `seed_demo` carga datos únicamente si la tabla `usuarios` está vacía:

```bash
python manage.py seed_demo
```

El archivo fuente es `infrastructure/seed/seed_demo.sql`. El comando también
restablece las secuencias de los modelos cargados.

Datos incluidos:

- 2 administradores.
- 6 vendedores.
- 6 categorías.
- 20 productos.
- Precios individuales y históricos.
- 4 proveedores.
- Compras, ventas, movimientos y pagos de ejemplo.

Usuarios de demostración:

```text
Administrador:
admin1@taller.com
admin2@taller.com

Vendedores:
vendedor1@taller.com
...
vendedor6@taller.com

Contraseña de todos: Password123!
```

En PostgreSQL, si cargas el SQL directamente en lugar de usar el comando,
ajusta las secuencias con:

```bash
psql -d sistema_taller -f infrastructure/seed/reset_sequences_postgres.sql
```

## Roles y permisos

### Administrador

- Puede administrar su propio catálogo, proveedores, usuarios vinculados y
  operaciones.
- Puede vender aunque no tenga inicialmente una fila separada de vendedor.
- Puede registrar ventas, compras y pagos.

### Vendedor

- Opera dentro de los vínculos aceptados con administradores.
- Puede acceder a las vistas y API permitidas por su sesión.
- Utiliza la moneda del administrador vinculado.

La sesión guarda `usuario_id`, `rol` y `nombre`. No se utiliza JWT.

## Rutas web

| Ruta | Descripción |
|---|---|
| `/` | Redirige a `/login/` |
| `/login/` | Inicio de sesión |
| `/register/` | Registro de administrador |
| `/dashboard/` | Dashboard según el rol |
| `/logout/` | Cierra la sesión y redirige al login |
| `/admin/` | Administración nativa de Django |

## API HTTP

La API utiliza autenticación por sesión, JSON y respuestas del manejador común
de excepciones.

### Autenticación y cuentas

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/usuarios/auth/login/` | Iniciar sesión |
| `POST` | `/api/usuarios/auth/logout/` | Cerrar sesión |
| `POST` | `/api/usuarios/auth/refresh/` | Compatibilidad con refresh; no usa JWT |
| `POST` | `/api/usuarios/registrar-admin/` | Registrar administrador |
| `POST` | `/api/usuarios/auth/registro/` | Alias de registro de administrador |
| `POST` | `/api/usuarios/registrar-vendedor/` | Registrar vendedor |
| `GET` | `/api/usuarios/get_user/admin/<admin_id>/vendedores/` | Vendedores vinculados |
| `GET`, `PATCH`, `DELETE` | `/api/usuarios/api/<usuario_id>/` | Detalle de usuario |
| `GET`, `PATCH` | `/api/usuarios/admin/perfil/` | Perfil del administrador |
| `GET`, `POST` | `/api/usuarios/solicitudes-admin/` | Solicitudes de vinculación |
| `GET`, `PATCH`, `DELETE` | `/api/usuarios/solicitudes-admin/<pk>/` | Detalle de solicitud |

### Categorías y productos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/inventario/categorias/select/` | Consultar o seleccionar categorías |
| `POST` | `/api/inventario/add_categoria/` | Crear categoría |
| `PUT`, `PATCH`, `DELETE` | `/api/inventario/categorias/<categoria_id>/` | Gestionar categoría |
| `GET`, `POST` | `/api/inventario/productos/` | Listar o crear productos |
| `GET` | `/api/inventario/productos/select_all/` | Seleccionar todos los productos |
| `GET` | `/api/inventario/productos/alertas/` | Consultar stock mínimo |
| `GET`, `PATCH`, `DELETE` | `/api/inventario/productos/<producto_id>/` | Gestionar producto |
| `GET` | `/api/inventario/productos/mas-vendidos/` | Productos más vendidos |
| `GET` | `/api/inventario/productos/vendidos/` | Productos vendidos |
| `GET` | `/api/inventario/history_productos/` | Historial de productos |

### Proveedores, inventario y reportes

| Método | Ruta | Descripción |
|---|---|---|
| `GET`, `POST` | `/api/inventario/proveedores/select/` | Proveedores |
| `GET`, `PATCH`, `DELETE` | `/api/inventario/proveedores/<proveedor_id>/` | Gestionar proveedor |
| `GET` | `/api/inventario/resumen/hoy/` | Resumen del día |
| `GET` | `/api/inventario/resumen/periodo/` | Resumen por período |
| `POST` | `/api/inventario/movimiento/entrada/` | Registrar entrada |
| `POST` | `/api/inventario/movimiento/salida/` | Registrar salida o venta |
| `GET` | `/api/inventario/movimiento/entrada/historial/` | Historial de entradas |
| `GET` | `/api/inventario/history_movimientos/<limite>/` | Últimos movimientos |
| `GET` | `/api/inventario/reportes/pdf/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` | Descargar reporte PDF |

### Ventas, compras y pagos

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/inventario/ventas/<venta_id>/anular/` | Anular venta |
| `POST` | `/api/inventario/compras/<compra_id>/anular/` | Anular compra |
| `GET`, `POST` | `/api/inventario/pagos/` | Crear o consultar pagos |

Los endpoints que escriben datos pasan por casos de uso y una unidad de trabajo
que abre una transacción atómica.

## Inventario y moneda

El inventario se representa mediante un kardex:

- entradas: compras y ajustes positivos;
- salidas: ventas y ajustes negativos;
- stock: suma de cantidades según el signo del movimiento;
- movimiento: registra administrador, producto, usuario responsable, motivo y
  fecha.

Las ventas pueden recibir un producto individual o una lista `items` con varias
líneas. Al confirmarse, el sistema valida el stock y genera los movimientos
correspondientes.

Los montos se trabajan con `Decimal`, no con punto flotante. Las cantidades se
redondean a tres decimales y el dinero a dos.

## Pruebas

Las pruebas actuales cubren reglas del dominio, sin requerir PostgreSQL:

```bash
python -m unittest discover -s tests -t .
```

También se puede usar pytest:

```bash
pytest
```

Para ejecutar una cobertura mínima de Django y del entorno:

```bash
python manage.py check
python manage.py dev_setup
pytest
```

## Comandos útiles

```bash
# Comprobar configuración
python manage.py check

# Preparar SQLite y ejecutar migraciones
python manage.py dev_setup

# Ejecutar el servidor
python manage.py runserver

# Ejecutar migraciones
python manage.py migrate

# Crear migraciones después de cambiar modelos
python manage.py makemigrations

# Cargar datos de demostración
python manage.py seed_demo

# Recopilar archivos estáticos
python manage.py collectstatic

# Consola administrativa
python manage.py shell
```

## Seguridad

El proyecto usa sesiones de Django y una clase de autenticación DRF basada en
esa sesión. El frontend existente no envía tokens JWT ni cookies CSRF en sus
`fetch`.

Por compatibilidad, algunas vistas usan `csrf_exempt`. Esto permite conservar
el comportamiento actual, pero no debe considerarse una configuración segura
para producción sin cambios adicionales.

Antes de desplegar:

- cambia `SECRET_KEY`;
- usa `DEBUG=0`;
- configura `ALLOWED_HOSTS`;
- habilita HTTPS y cookies seguras;
- añade protección CSRF compatible con el frontend;
- usa contraseñas reales y límites de intentos;
- configura Sentry solo con una instancia autorizada;
- limita el acceso a administración Django;
- usa PostgreSQL con usuario y permisos separados;
- revisa las variables y secretos de producción;
- verifica permisos y límites en todos los endpoints.

## Problemas frecuentes

### Django abre SQLite aunque esperaba PostgreSQL

El sistema selecciona PostgreSQL solo si `POSTGRES_DB` tiene un valor. Revisa
el `.env` y elimina o comenta esa variable para SQLite.

### Faltan tablas o triggers

- En SQLite: ejecuta `python manage.py dev_setup`.
- En PostgreSQL: aplica `infrastructure/sql/001_schema.sql` y luego
  `python manage.py migrate --fake-initial`.

### Los datos demo indican que `usuarios` ya tiene datos

`seed_demo` requiere una base sin usuarios. Prepara una base nueva o elimina los
datos existentes antes de cargar el SQL.

### Error al generar PDF

Comprueba que las librerías nativas requeridas por WeasyPrint estén instaladas
en el sistema operativo. Este requisito puede variar entre Windows, Linux y
macOS.

### No se visualizan archivos estáticos

Ejecuta `python manage.py collectstatic` para producción y confirma que
`STATIC_ROOT`, `STATICFILES_DIRS` y el servidor están configurados
correctamente. En desarrollo, Django puede servirlos mediante `staticfiles`.
