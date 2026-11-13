import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON, postJSON, putJSON, deleteJSON } from '../../shared/core/http.js';

export const fetchProductos = () => getJSON(ENDPOINTS.productosSelect);

export const fetchCategorias = () => getJSON(ENDPOINTS.categorias);

export const eliminarProducto = (id) => deleteJSON(ENDPOINTS.productoDetail(id));

export function guardarProducto(payload, esEdicion) {
  if (esEdicion) {
    return putJSON(ENDPOINTS.productoDetail(payload.id), payload);
  }
  return postJSON(ENDPOINTS.productos, payload);
}
