# sistema_taller

## API — Usuarios

### Registro

**`POST /usuarios/register/`** — público

```json
{"username": "juan", "email": "juan@example.com", "password": "secret123"}
```
```json
{"uuid": "550e8400-...", "message": "Usuario registrado exitosamente"}
```

### Inicio de sesión

**`POST /usuarios/login/`** — público

```json
{"email": "juan@example.com", "password": "secret123"}
```
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "usuario": {"id": "550e...", "nombre": "juan", "email": "juan@example.com", "rol": "vendedor"}
}
```

Usar el `access` como `Authorization: Bearer <token>` en los endpoints protegidos.

### CRUD (requiere JWT)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/usuarios/api/` | Listar usuarios |
| `GET` | `/usuarios/api/{uuid}/` | Detalle de usuario |
| `PUT`/`PATCH` | `/usuarios/api/{uuid}/` | Actualizar usuario |
| `DELETE` | `/usuarios/api/{uuid}/` | Eliminar usuario |

**Ejemplo listar:**
```
GET /usuarios/api/
Authorization: Bearer eyJ...
```
```json
[{"uuid": "550e...", "username": "juan", "email": "juan@example.com", "rol": "vendedor", "activo": true, "fecha_creacion": "..."}]
```

### Errores comunes

| Código | Cuerpo | Significado |
|---|---|---|
| 400 | `{"campo": "Este campo es obligatorio"}` | Falta campo requerido |
| 400 | `{"detail": "El email 'x' ya está registrado"}` | Email duplicado |
| 401 | `{"detail": "Credenciales inválidas"}` | Login fallido |
| 403 | `{"detail": "Usuario inactivo..."}` | Cuenta desactivada |
| 500 | `{"error": "Error interno del servidor"}` | Error inesperado |