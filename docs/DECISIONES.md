# Decisiones de arquitectura y reconstrucción

Este documento registra las decisiones tomadas durante la reconstrucción del
backend. Cada decisión intenta explicar el contexto, la alternativa elegida y
sus consecuencias.

## ADR-001. Rama nueva y front-end intacto

**Contexto.** El backend anterior mezclaba Django, reglas de negocio y acceso a
datos. Se pidió reconstruir la base y el dominio sin tocar el front-end.

**Decisión.** Crear la rama `rewrite/hexagonal-domain` desde `main`. Eliminar el
backend anterior y conservar `templates/` y `static/`. Mantener únicamente el
bootstrap mínimo de Django (`config/`, `manage.py`, `requirements.txt`).

**Consecuencias.** El front-end sigue siendo la referencia del contrato HTTP.
Las vistas y APIs se reconstruyen para que el JavaScript existente siga
funcionando.

## ADR-002. Arquitectura hexagonal

**Contexto.** Se necesita separar las reglas del negocio de Django.

**Decisión.** Organizar el código en tres zonas:

- `core/domain`: entidades, value objects, enums, errores y reglas. No importa
  Django.
- `core/application`: puertos de repositorios, unidad de trabajo y casos de uso.
- `apps/`: adaptadores Django (ORM, autenticación, vistas HTTP).

**Consecuencias.** El dominio puede probarse sin base de datos. Los cambios de
persistencia no obligan a reescribir reglas.

## ADR-003. El esquema SQL es la fuente de verdad

**Contexto.** El esquema PostgreSQL entregado define claves compuestas, índices
parciales y triggers que Django no representa de forma directa.

**Decisión.** Guardar el esquema en `infrastructure/sql/001_schema.sql` y
declarar los modelos Django con `managed = False`. Django no crea ni migra esas
tablas; las crea el SQL.

**Consecuencias.** `manage.py migrate` solo administra las tablas propias de
Django (auth, sesiones, admin). Para el sistema hay que aplicar el SQL. Las
restricciones compuestas y los triggers quedan garantizados por PostgreSQL.

## ADR-004. Identificadores enteros

**Contexto.** El esquema usa `SERIAL` para las entidades del negocio.

**Decisión.** El dominio y los puertos usan `int | None` para los identificadores
nuevos. No se introducen UUID para las entidades del negocio.

**Consecuencias.** El front-end recibe enteros; donde espera `uuid` se devuelve
el mismo identificador como texto para conservar el contrato.

## ADR-005. Autenticación por sesión

**Contexto.** El front-end hace `fetch` con `credentials: 'include'` y espera que
`/dashboard` funcione con una cookie. No inspecciona tokens JWT.

**Decisión.** Usar sesiones de Django y una autenticación DRF basada en la
sesión. El login guarda `usuario_id`, `rol` y `nombre` en la sesión. No se usa
SimpleJWT.

**Consecuencias.** Se elimina la dependencia de JWT. La cookie `sessionid` es la
que autentica tanto páginas como API. El endpoint de refresh queda como no-op
para compatibilidad.

## ADR-006. Pagos como dominio separado

**Contexto.** El esquema tiene una tabla `pagos`. El front-end no tiene todavía
una pantalla de cobros.

**Decisión.** Crear `core/domain/payments` y `apps.payments`, en lugar de meter
`Pago` dentro de ventas. La relación con la venta se hace por identificador.

**Consecuencias.** Se puede crecer la lógica de cobros sin tocar ventas. La
validación de que la suma de pagos no supere el total se hace en el caso de uso.

## ADR-007. Dinero y cantidades con Decimal

**Contexto.** PostgreSQL usa `NUMERIC(12,2)` y `NUMERIC(12,3)`.

**Decisión.** Usar `Decimal` en los value objects `Money` y `Quantity`. `Money`
redondea a dos decimales y no admite montos negativos. `Quantity` exige valores
mayores que cero y redondea a tres decimales.

**Consecuencias.** Se evitan errores de punto flotante. Las cantidades de stock y
las líneas de venta/compra comparten la misma representación.

## ADR-008. Stock calculado, no almacenado

**Contexto.** El esquema define un kardex en `movimiento_inventario`.

**Decisión.** El stock es la suma con signo de los movimientos. No se agrega una
columna `stock_actual` a `productos`.

**Consecuencias.** El stock siempre es auditable. Las lecturas agregan
movimientos; se compensa con índices y, si hace falta, una vista materializada.

## ADR-009. Compatibilidad con el contrato del front-end

**Contexto.** El front-end existente espera campos que el esquema nuevo no tiene
o tiene con otro nombre.

**Decisión.** Mantener el contrato HTTP y adaptar la infraestructura:

- `productos.stock_minimo` se agrega al esquema para conservar el formulario y
  las alertas.
- `ventas.canal_venta` se agrega al esquema para conservar el canal de la venta
  rápida.
- `precio_unitario` en las respuestas se obtiene de la tarifa vigente
  `individual`; no vive en `productos`.
- `uuid` en las respuestas de usuarios es el identificador entero serializado
  como texto.
- `cantidad_inicial` se registra como movimiento de ajuste positivo.

**Consecuencias.** El front-end no necesita cambios. El esquema se aparta de la
versión original en esos tres puntos, documentados aquí.

## ADR-010. Compras con usuario responsable

**Contexto.** El trigger original de compras usaba
`(SELECT u.id FROM usuarios LIMIT 1)`, un usuario arbitrario.

**Decisión.** Agregar `compras.usuario_id` como referencia obligatoria a
`usuarios` y usarlo en el movimiento de entrada.

**Consecuencias.** El kardex registra correctamente quién confirmó la compra.

## ADR-011. Borrado y anulación

**Contexto.** El esquema original solo impedía borrar ventas confirmadas.

**Decisión.** Impedir el borrado de ventas y compras confirmadas. La anulación
es un cambio de estado; la reversión de stock se implementa en el caso de uso de
anulación.

**Consecuencias.** No se pierde historia. La anulación genera los movimientos
inversos correspondientes.

## ADR-012. Validación de stock al confirmar

**Contexto.** El trigger original de stock se ejecutaba al insertar líneas, pero
las líneas se insertan cuando la venta todavía es borrador. En la práctica nunca
validaba.

**Decisión.** Validar el stock en un trigger `BEFORE UPDATE` sobre `ventas`,
cuando el estado pasa a `confirmada`, recorriendo todas las líneas.

**Consecuencias.** La confirmación falla si no hay stock suficiente. La lógica
de dominio también expone `verificar_stock_suficiente` para el caso de uso.

## ADR-013. Fechas

**Decisión.** Usar `datetime` con zona horaria UTC en el dominio. Django se
configura con `USE_TZ = True` y `TIME_ZONE = "America/La_Paz"` para presentación.
Las columnas de fecha del esquema usan `TIMESTAMPTZ`, no `TIMESTAMP`, porque
Django con `USE_TZ=True` espera instantes con zona horaria y PostgreSQL debe
preservar el instante original.

**Consecuencias.** Los cálculos y comparaciones son consistentes; la
presentación se adapta a la zona local. Los `TIMESTAMP` sin zona del esquema
original producían corrimientos de fecha al filtrar por día.

## ADR-014. Pruebas

**Decisión.** Probar el dominio con `unittest` (compatible con `pytest`) sin
necesidad de base de datos. Las pruebas de infraestructura se agregan cuando los
adaptadores estén completos.

**Consecuencias.** `python -m unittest discover -s tests` y `pytest` deben
funcionar sin PostgreSQL.

## ADR-015. PDF con WeasyPrint

**Contexto.** El front-end descarga un PDF de reporte por período.

**Decisión.** Mantener WeasyPrint y una plantilla HTML de reporte en
`templates/inventario/reporte_periodo_pdf.html`.

**Consecuencias.** Se conserva la exportación PDF existente. WeasyPrint requiere
las dependencias del sistema que ya estaban documentadas en el proyecto.

## ADR-016. Casos de uso y UnitOfWork

**Contexto.** Los views no deben contener reglas de negocio ni transacciones
sueltas.

**Decisión.** Cada flujo de escritura se implementa como un caso de uso en
`core/application`. Los casos de uso reciben un `UnitOfWork` y un
`PasswordHasher` por inyección. La implementación `DjangoUnitOfWork` agrupa los
repositorios y abre una transacción atómica.

**Consecuencias.** Los views solo traducen HTTP a entrada del caso de uso y
salida a JSON. Las pruebas de aplicación pueden usar un UnitOfWork falso.

## ADR-017. Un administrador también puede vender

**Contexto.** El front-end tiene la misma pantalla de venta para administrador y
vendedor. El esquema exige que `ventas.vendedor_id` referencie `vendedores`.

**Decisión.** Si un administrador registra una venta y no tiene fila de
vendedor, se crea automáticamente su subtipo `vendedores` y un vínculo aceptado
consigo mismo. Ese vendedor automático se excluye de la lista de vendedores
gestionados.

**Consecuencias.** El administrador puede vender sin cambiar el front-end. La
tabla `vendedores` puede contener al mismo usuario que `administradores`; el
esquema ya lo permite.

## ADR-018. Sesión sin CSRF por compatibilidad

**Contexto.** El JavaScript existente hace `fetch` con `credentials: 'include'`
pero no envía token CSRF. Las vistas de DRF son `csrf_exempt`.

**Decisión.** Autenticar por sesión de Django y aceptar POST/PATCH/DELETE sin
token CSRF para conservar el front-end.

**Consecuencias.** Funciona con el cliente actual, pero es una debilidad de
seguridad si el sistema se expone a terceros. Antes de producción hay que
agregar CSRF o cambiar el front-end para obtener y enviar el token.

## ADR-019. Consultas de lectura en infraestructura

**Contexto.** Reportes, historial y alertas requieren joins y agregaciones que
no pertenecen al dominio.

**Decisión.** Implementar esas lecturas como read models en
`apps/catalog/queries.py`, usando el ORM. Las escrituras siguen pasando por
casos de uso y repositorios.

**Consecuencias.** El dominio queda puro y las consultas pueden optimizarse sin
tocar reglas. Es una separación práctica tipo CQRS ligero.

## ADR-020. Contrato de identificadores del front-end

**Contexto.** El JavaScript de usuarios usa el campo `uuid` como identificador
para editar y eliminar.

**Decisión.** Devolver `uuid` como el identificador entero serializado a texto.
Las rutas aceptan enteros.

**Consecuencias.** El front-end no necesita cambios. El nombre `uuid` es
heredado y no implica que el identificador sea un UUID real.

## ADR-021. Vínculos N:M y aceptación múltiple

**Contexto.** El texto de la pantalla del vendedor dice que al aceptar un
administrador "los demás quedan bloqueados". El esquema y las reglas del negocio
permiten que un vendedor trabaje para varios administradores.

**Decisión.** Respetar el esquema N:M: aceptar un vínculo no inactiva los demás.
La pantalla y los endpoints listan todos los vínculos.

**Consecuencias.** El texto de la interfaz quedó desactualizado respecto del
modelo. Si se quiere el comportamiento de un solo administrador, hay que
cambiarlo en el dominio y en el esquema, no solo en la vista.

## ADR-022. Vendedor con varios administradores

**Contexto.** El esquema permite que un vendedor tenga varios vínculos
aceptados. El front-end de ventas no envía el administrador al que pertenece la
operación.

**Decisión.** El vendedor opera contra el primer vínculo aceptado. Si el cliente
envía `admin_id` en el cuerpo o en la query, se usa ese vínculo si está
aceptado.

**Consecuencias.** Con varios administradores el comportamiento por defecto es
determinista pero puede no ser el esperado. Una interfaz futura debería permitir
elegir el administrador activo.

## ADR-023. Errores de API

**Decisión.** Los errores de dominio se traducen a HTTP con un handler global:
400 validación/regla de negocio, 401 credenciales, 403 permisos, 404 no
encontrado y 409 conflicto. El cuerpo incluye `detail`, `code` y `context`.
Los endpoints de registro devuelven además `{ "error": { "message", "code",
"details" } }` porque el JavaScript de registro consume esa forma.

**Consecuencias.** El front-end recibe mensajes útiles sin acoplarse a
excepciones de Django.

## ADR-024. Conexión del front-end con la API

**Contexto.** Algunas pantallas existían en el HTML pero no tenían JavaScript
que las conectara: proveedores, solicitudes del vendedor y acciones del
administrador sobre solicitudes pendientes.

**Decisión.** Se agregaron módulos JavaScript siguiendo el patrón existente:

- `static/js/admin/proveedores/`: CRUD de proveedores usando
  `/api/inventario/proveedores/`.
- `static/js/vendedor/solicitudes/`: envío, listado y cancelación de solicitudes
  usando `/api/usuarios/solicitudes-admin/`.
- `static/js/admin/usuarios/`: botones Aceptar/Rechazar para solicitudes
  pendientes.

También se agregó el enlace de Proveedores al menú del administrador y se
actualizó el texto del vendedor para reflejar el modelo N:M.

**Consecuencias.** Las pantallas que ya existían quedaron funcionales. La
sección de Configuración sigue siendo un placeholder porque no tiene enlace de
menú y el esquema solo guarda `nombre_negocio` del administrador.

## ADR-025. Lista de vendedores por vínculo aceptado

**Contexto.** La lista de vendedores de un administrador incluía vínculos
pendientes y al propio administrador cuando había vendido, duplicando filas en
la pantalla de usuarios.

**Decisión.** `listar_por_administrador` filtra por estado `aceptado` y excluye
el identificador del propio administrador. La edición y el borrado de vendedores
también exigen un vínculo aceptado.

**Consecuencias.** La bandeja de solicitudes pendientes muestra solo solicitudes,
y la tabla de vendedores muestra solo vínculos efectivos.

## ADR-026. Esquema de desarrollo para SQLite

**Contexto.** El sistema usa PostgreSQL en producción, pero el comando
`python manage.py runserver` sin variables de entorno cae en SQLite. SQLite no
tiene las tablas del negocio porque los modelos Django son `managed = False`, y
el error resultante era `no such table: usuarios`.

**Decisión.** Mantener PostgreSQL como fuente de verdad y agregar un esquema de
desarrollo para SQLite:

- `ensure_sqlite_schema()` crea las tablas unmanaged con
  `schema_editor.create_model` y agrega las columnas nuevas que falten.
- Se crean triggers SQLite equivalentes para recalcular totales, generar
  movimientos al confirmar y bloquear el borrado de documentos confirmados.
- El comando `dev_setup` ejecuta `migrate` y prepara el esquema.
- Un comando `runserver` propio, activo solo con `DEBUG=True` y SQLite, ejecuta
  `migrate` y `ensure_sqlite_schema()` antes de arrancar.
- El hook `post_migrate` también crea el esquema, así que `migrate` alcanza.

La validación de stock y de tarifa vigente se mantiene en los casos de uso. Los
triggers SQLite no replican esas validaciones para evitar SQL frágil; PostgreSQL
sí las tiene a nivel de base.

**Consecuencias.** `python manage.py runserver` funciona en desarrollo sin
PostgreSQL. En producción se sigue aplicando `infrastructure/sql/001_schema.sql`.
Los triggers de SQLite son una ayuda de desarrollo; no reemplazan la garantía de
PostgreSQL.

## ADR-027. Moneda por administrador y por operación

**Contexto.** La pantalla de configuración tenía un selector de moneda, pero no
existía en el esquema. A su vez, las ventas y compras guardaban solo números, sin
moneda, así que un pago no podía reconstruir la moneda de la venta.

**Decisión.** Agregar `moneda` a `administradores`, `ventas`, `compras` y
`pagos`. La moneda del administrador se usa para las tarifas nuevas y para los
costos de entrada. Cada venta/compra/pago conserva la moneda con la que se
registró. Las respuestas de productos incluyen la moneda de su tarifa vigente, y
el front-end formatea cada precio con su propia moneda.

**Consecuencias.** Cambiar la moneda del administrador no convierte precios
históricos: las tarifas viejas mantienen su moneda y se muestran correctamente.
Las nuevas tarifas usan la moneda configurada.

## ADR-028. Configuración del administrador conectada

**Decisión.** Se agregó `GET/PATCH /api/usuarios/admin/perfil/` para leer y
actualizar `nombre_negocio` y `moneda`. El enlace Configuración se agregó al menú
del administrador y el formulario se conectó con ese endpoint.

**Consecuencias.** La sección que antes era un placeholder ahora funciona. El
cambio de moneda recarga la página para actualizar el formato global.

## ADR-029. Se eliminó la sección legacy de inventario del admin

**Contexto.** La plantilla del administrador tenía una sección `#inventario` con
filtros y tabla, pero no estaba enlazada en el menú y no tenía JavaScript. La
sección `#productos` ya cubre el inventario.

**Decisión.** Eliminar la sección legacy del HTML del administrador. La pantalla
de inventario del vendedor se conserva.

**Consecuencias.** Se reduce el HTML muerto y no se duplica la lógica de
inventario.

## ADR-030. Endpoints de anulación y pagos sin interfaz

**Decisión.** Agregar endpoints para anular ventas/compras y para listar/crear
pagos, usando los casos de uso existentes. No se agregó interfaz porque el
front-end actual no tiene pantallas de cobro ni de anulación.

**Consecuencias.** La API queda completa para una interfaz futura. Las
anulaciones generan movimientos inversos y los pagos validan que la suma no
supere el total de la venta.
