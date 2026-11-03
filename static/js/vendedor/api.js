import { ENDPOINTS } from '../shared/core/config.js';
import { getJSON } from '../shared/core/http.js';

export const obtenerAlertasStock = () => getJSON(ENDPOINTS.productosAlertas);

export const obtenerProductos = () => getJSON(ENDPOINTS.productosSelect);

export const obtenerCategorias = () => getJSON(ENDPOINTS.categorias);

