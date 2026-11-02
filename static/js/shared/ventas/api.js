import { ENDPOINTS } from '../core/config.js';
import { getJSON } from '../core/http.js';

export const obtenerProductos = () => getJSON(ENDPOINTS.productosSelect);
