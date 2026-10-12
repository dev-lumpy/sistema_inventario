// static/js/admin/categorias/js/core/api.js

/* ============================================================
   PARTE 1 — Endpoints
   ============================================================ */

/** POST — Crear una categoría nueva (body: { nombre }). */
const API_CATEGORIA_CREATE = '/api/inventario/add_categoria';

/** GET — Todas las categorías. */
const API_CATEGORIA_LIST = '/api/inventario/categorias/select';


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
