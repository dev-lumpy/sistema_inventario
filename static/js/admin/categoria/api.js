// static/js/admin/categorias/js/core/api.js

/* ============================================================
   PARTE 1 — Endpoints
   ============================================================ */

/** POST — Crear una categoría nueva (body: { nombre }). */
const API_CATEGORIA_CREATE = '/api/inventario/add_categoria';

/** GET — Todas las categorías. */
const API_CATEGORIA_LIST = '/api/inventario/categorias/select';

/** PUT — Editar una categoría existente (body: { nombre }). */
const API_CATEGORIA_UPDATE = (id) => `/api/inventario/categorias/${id}`;

/** DELETE — Eliminar una categoría existente. */
const API_CATEGORIA_DELETE = (id) => `/api/inventario/categorias/${id}`;


/* ============================================================
   PARTE 2 — Funciones
   ============================================================ */

/**
 * Crea una categoría con el nombre indicado.
 * @param {string} nombre
 * @returns {Promise<{id:number, nombre:string}>}
 */
export async function postCategoria(nombre) {
  const res = await fetch(API_CATEGORIA_CREATE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ nombre }),
  });

  if (!res.ok) {
    let detalle = null;
    try { detalle = await res.json(); } catch {}
    throw new Error(detalle?.nombre?.[0] || `No se pudo crear la categoría (${res.status}).`);
  }

  return res.json();
}

/**
 * Trae todas las categorías.
 * @returns {Promise<Array<{id:number, nombre:string}>>}
 */
export async function getCategorias() {
  const res = await fetch(API_CATEGORIA_LIST, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!res.ok) throw new Error(`No se pudieron cargar las categorías (${res.status}).`);

  return res.json();
}

/**
 * Actualiza el nombre de una categoría existente.
 * @param {number} id
 * @param {string} nombre
 * @returns {Promise<{id:number, nombre:string}>}
 */
export async function updateCategoria(id, nombre) {
  const res = await fetch(API_CATEGORIA_UPDATE(id), {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ nombre }),
  });

  if (!res.ok) {
    let detalle = null;
    try { detalle = await res.json(); } catch {}
    throw new Error(detalle?.nombre?.[0] || `No se pudo actualizar la categoría (${res.status}).`);
  }

  return res.json();
}

/**
 * Elimina una categoría existente.
 * @param {number} id
 * @returns {Promise<void>}
 */
export async function deleteCategoria(id) {
  const res = await fetch(API_CATEGORIA_DELETE(id), {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  // 204 No Content → no hay body que parsear
  if (res.status === 204) return;

  if (!res.ok) {
    let detalle = null;
    try { detalle = await res.json(); } catch {}
    throw new Error(detalle?.detail || detalle?.nombre?.[0] || `No se pudo eliminar la categoría (${res.status}).`);
  }

  // Por si el backend devuelve 200 con un body
  try { return await res.json(); } catch { return; }
}
