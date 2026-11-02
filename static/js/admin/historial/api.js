import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON } from '../../shared/core/http.js';

export const getProductos = () => getJSON(ENDPOINTS.historialProductos);

export const getMovimientos = () => getJSON(ENDPOINTS.historialMovimientos);
