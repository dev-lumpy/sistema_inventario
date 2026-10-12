// static/js/admin/entrada_stock/js/services/entrada.service.js
import { CONFIG } from '../core/config.js';
import { getJSON, postJSON } from '../core/http.js';

export function obtenerProductos() {
  return getJSON(CONFIG.ENDPOINTS.productosSelect);
}

export function obtenerProveedores() {
  return getJSON(CONFIG.ENDPOINTS.proveedoresSelect);
}

export function registrarEntrada({ producto_id, cantidad, proveedor_id }) {
  return postJSON(CONFIG.ENDPOINTS.registrarEntrada, {
    producto: producto_id,   // ← ojo con el nombre del campo, ver abajo
    cantidad,
    proveedor: proveedor_id,
  });
}

export function obtenerHistorial() {
  return getJSON(CONFIG.ENDPOINTS.historialEntradas);
}
