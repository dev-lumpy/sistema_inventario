from .base import Language, MessageKey


class UserES(MessageKey):
    LANGUAGE = Language.SPANISH

    # ─── Genéricos ───────────────────────────────────────
    NOT_FOUND          = "Usuario {usuario_id} no encontrado"
    ID_INVALID         = "ID de usuario inválido: {usuario_id}"
    INACTIVE           = "El usuario {usuario_id} está inactivo"

    # ─── UsuarioId (UUID) ────────────────────────────────
    ID_NULL            = "El ID de usuario no puede ser nulo"
    ID_EMPTY           = "El ID de usuario no puede estar vacío"
    ID_FORMAT          = "El ID de usuario tiene un formato inválido: {usuario_id}"
    ID_TYPE            = "El ID de usuario debe ser un texto o UUID, no {tipo}"

    # ─── Nombre ──────────────────────────────────────────
    NOMBRE_INVALIDO    = "El nombre de usuario no es válido"
    NOMBRE_VACIO       = "El nombre de usuario no puede estar vacío"
    NOMBRE_MUY_CORTO   = "El nombre de usuario es demasiado corto (mínimo {minimo} caracteres)"
    NOMBRE_MUY_LARGO   = "El nombre de usuario es demasiado largo (máximo {maximo} caracteres)"
    NOMBRE_FORMATO     = "El nombre de usuario contiene caracteres no permitidos"

    # ─── Email ───────────────────────────────────────────
    EMAIL_INVALIDO     = "El email no tiene un formato válido: {email}"
    EMAIL_VACIO        = "El email no puede estar vacío"
    EMAIL_DUPLICADO    = "El email {email} ya está registrado"

    # ─── Password ────────────────────────────────────────
    PASSWORD_INVALIDO  = "La contraseña no es válida"
    PASSWORD_VACIA     = "La contraseña no puede estar vacía"
    PASSWORD_MUY_CORTA = "La contraseña debe tener al menos {minimo} caracteres"
    PASSWORD_MUY_LARGA = "La contraseña es demasiado larga (máximo {maximo} caracteres)"
    PASSWORD_DEBIL     = "La contraseña es demasiado débil"

    # ─── Admin / Roles ───────────────────────────────────
    ADMIN_NOT_FOUND    = "Administrador {admin_id} no encontrado"
    NOT_ADMIN          = "El usuario {usuario_id} no tiene permisos de administrador"
    ROL_INVALIDO       = "El rol '{rol}' no es válido"


class UserEN(MessageKey):
    LANGUAGE = Language.ENGLISH

    # ─── Genéricos ───────────────────────────────────────
    NOT_FOUND          = "User {usuario_id} not found"
    ID_INVALID         = "Invalid user ID: {usuario_id}"
    INACTIVE           = "User {usuario_id} is inactive"

    # ─── UsuarioId (UUID) ────────────────────────────────
    ID_NULL            = "User ID cannot be null"
    ID_EMPTY           = "User ID cannot be empty"
    ID_FORMAT          = "User ID has an invalid format: {usuario_id}"
    ID_TYPE            = "User ID must be a string or UUID, not {tipo}"

    # ─── Nombre ──────────────────────────────────────────
    NOMBRE_INVALIDO    = "Username is not valid"
    NOMBRE_VACIO       = "Username cannot be empty"
    NOMBRE_MUY_CORTO   = "Username is too short (min {minimo} characters)"
    NOMBRE_MUY_LARGO   = "Username is too long (max {maximo} characters)"
    NOMBRE_FORMATO     = "Username contains invalid characters"

    # ─── Email ───────────────────────────────────────────
    EMAIL_INVALIDO     = "Email has an invalid format: {email}"
    EMAIL_VACIO        = "Email cannot be empty"
    EMAIL_DUPLICADO    = "Email {email} is already registered"

    # ─── Password ────────────────────────────────────────
    PASSWORD_INVALIDO  = "Password is not valid"
    PASSWORD_VACIA     = "Password cannot be empty"
    PASSWORD_MUY_CORTA = "Password must be at least {minimo} characters"
    PASSWORD_MUY_LARGA = "Password is too long (max {maximo} characters)"
    PASSWORD_DEBIL     = "Password is too weak"

    # ─── Admin / Roles ───────────────────────────────────
    ADMIN_NOT_FOUND    = "Admin {admin_id} not found"
    NOT_ADMIN          = "User {usuario_id} does not have admin permissions"
    ROL_INVALIDO       = "Role '{rol}' is not valid"


# Esto es lo que _discover() busca:
ENTITY = "user"
CATALOGS = {
    Language.SPANISH: UserES,
    Language.ENGLISH: UserEN,
}
