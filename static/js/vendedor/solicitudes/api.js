import { ENDPOINTS } from '../../shared/core/config.js';
import { deleteJSON, getJSON, postJSON } from '../../shared/core/http.js';

export const listarSolicitudes = () => getJSON(ENDPOINTS.solicitudesAdmin);

export const crearSolicitud = (payload) => postJSON(ENDPOINTS.solicitudesAdmin, payload);

export const cancelarSolicitud = (id) => (
  deleteJSON(ENDPOINTS.solicitudAdminDetail(id))
);
