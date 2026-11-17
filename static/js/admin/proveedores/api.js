import { ENDPOINTS } from '../../shared/core/config.js';
import { deleteJSON, getJSON, postJSON, putJSON } from '../../shared/core/http.js';

export const listarProveedores = () => getJSON(ENDPOINTS.proveedoresSelect);

export const crearProveedor = (payload) => postJSON(ENDPOINTS.proveedoresSelect, payload);

export const actualizarProveedor = (id, payload) => (
  putJSON(ENDPOINTS.proveedorDetail(id), payload)
);

export const eliminarProveedor = (id) => deleteJSON(ENDPOINTS.proveedorDetail(id));
