// static/js/admin/entrada_stock/js/core/api.js

/* ============================================================
   PARTE 1 — Endpoints
   ============================================================ */

/** GET — Todos los productos activos (id, nombre, precio, stock, etc.). */
const API_PRODUCTOS = '/api/inventario/history_productos';

/** GET — Todos los movimientos de stock (entradas registradas). */
const API_MOVIMIENTOS_STOCK = '/api/inventario/history_movimientos';


/* ============================================================
   PARTE 2 — Funciones que consumen los endpoints
   ============================================================ */

/**
 * Trae todos los productos activos.
 * @returns {Promise<Array<{id:number, nombre:string, precio_unitario:string, stock_minimo:number, stock_actual:number, activo:boolean}>>}
 */
export async function getProductos() {
  const res = await fetch(API_PRODUCTOS, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error(`No se pudieron cargar los productos (${res.status}).`);
  }

  const data = await res.json();
  return data;
}

/**
 * Trae todos los movimientos de stock registrados.
 * @returns {Promise<Array<{id:number, fecha:string, producto:string, proveedor:string|null, tipo:string, motivo:string, cantidad:number, detalle:string}>>}
 */
export async function getMovimientosStock() {
  const res = await fetch(API_MOVIMIENTOS_STOCK, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!res.ok) throw new Error(`No se pudieron cargar los movimientos (${res.status}).`);

  const data = await res.json();
  return data;
}
