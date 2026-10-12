/* api.js — Todo lo que habla con el backend. Si cambia una ruta, es acá. */

const URL = {
  productos: '/api/inventario/productos',
  productosTodos: '/api/inventario/productos/select_all',
  categorias: '/api/inventario/categorias/select',
};

async function safeJson(res) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

/** Hace el fetch y traduce los errores HTTP a mensajes entendibles. */
async function apiFetch(url, opciones, contexto) {
  let res;
  try {
    res = await fetch(url, opciones);
  } catch (err) {
    console.error(`[${contexto}] Error de red:`, err);
    throw new Error('No hay conexión con el servidor.');
  }

  if (!res.ok) {
    const detalle = await safeJson(res);
    console.error(`[${contexto}] HTTP ${res.status}:`, detalle);

    if (res.status >= 500) throw new Error('Error del servidor. Intentá de nuevo más tarde.');
    if (res.status === 401 || res.status === 403) throw new Error('No tenés permiso para esta acción.');
    if (res.status === 404) throw new Error('No se encontró el recurso solicitado.');
    if (res.status >= 400) throw new Error('Solicitud inválida. Revisá los datos.');
    throw new Error(`Respuesta inesperada del servidor (${res.status}).`);
  }

  try {
    return await res.json();
  } catch (err) {
    console.error(`[${contexto}] La respuesta no era JSON válido:`, err);
    throw new Error('Respuesta inválida del servidor.');
  }
}

export function fetchProductos() {
  return apiFetch(URL.productosTodos, undefined, 'fetchProductos');
}

export function fetchCategorias() {
  return apiFetch(URL.categorias, undefined, 'fetchCategorias');
}

export function guardarProducto(payload, esEdicion) {
  const url = esEdicion ? `${URL.productos}/${payload.id}` : URL.productos;
  return apiFetch(
    url,
    {
      method: esEdicion ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    'guardarProducto'
  );
}

export async function eliminarProducto(id) {
  // TODO: reemplazar por el endpoint real cuando exista.
  // return apiFetch(`${URL.productos}/${id}`, { method: 'DELETE' }, 'eliminarProducto');
  console.log('[api.js] eliminarProducto (simulado):', id);
  return true;
}


// Solo para debug. En producción se puede borrar.
if (typeof window !== 'undefined') {
  window.api = { fetchProductos, fetchCategorias, eliminarProducto, apiFetch };
}
