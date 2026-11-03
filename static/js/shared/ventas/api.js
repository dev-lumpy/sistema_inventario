import { ENDPOINTS } from '../core/config.js';
import { getJSON, postJSON } from '../core/http.js';

export const obtenerProductos = () => getJSON(ENDPOINTS.productosSelect);

/*
    * Realizar una venta con estos 3 datos
    * 1. Producto
    * 2. Cantidad
    * 3. Canal
*/
export const addMovimientoStock = (body) => postJSON(ENDPOINTS.salidaStock, body);

