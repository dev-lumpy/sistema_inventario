import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON, postJSON } from '../../shared/core/http.js';

export const obtenerProductos = () => getJSON(ENDPOINTS.productosSelect);

export const obtenerProveedores = () => getJSON(ENDPOINTS.proveedoresSelect);

export const registrarEntrada = ({ producto_id, cantidad, proveedor_id }) => postJSON(
  ENDPOINTS.entradaStock,
  {
    producto: producto_id,
    cantidad: Number(cantidad),
    proveedor: proveedor_id,
  },
);

export const obtenerHistorial = () => getJSON(ENDPOINTS.entradaHistorial);
