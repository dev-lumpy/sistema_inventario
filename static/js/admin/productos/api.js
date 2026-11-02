import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON, postJSON, putJSON } from '../../shared/core/http.js';

export const fetchProductos = () => getJSON(ENDPOINTS.productosSelect);

export const fetchCategorias = () => getJSON(ENDPOINTS.categorias);

export function guardarProducto(payload, esEdicion) {
  if (esEdicion) {
    return putJSON(ENDPOINTS.productoDetail(payload.id), payload);
  }
  return postJSON(ENDPOINTS.productos, payload);
}
