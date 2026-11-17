import { CONFIG } from '../../shared/core/config.js';
import { deleteJSON, getJSON, patchJSON, postJSON } from '../../shared/core/http.js';

const base = () => CONFIG.USUARIOS;

const urlVendedores = (adminId) => (
  `${base()}/get_user/admin/${adminId}/vendedores/`
);

const urlUsuario = (uuid) => `${base()}/api/${uuid}/`;

export const crearVendedor = (payload) => (
  postJSON(`${base()}/registrar-vendedor/`, payload)
);

export const listarVendedores = (adminId) => getJSON(urlVendedores(adminId));

export const listarSolicitudes = (adminId) => (
  getJSON(`${base()}/solicitudes-admin/?admin_id=${adminId}&estado=pendiente`)
);

export const actualizarUsuario = (uuid, payload) => (
  patchJSON(urlUsuario(uuid), payload)
);

export const eliminarUsuario = (uuid) => deleteJSON(urlUsuario(uuid));

export const responderSolicitud = (id, payload) => (
  patchJSON(`${base()}/solicitudes-admin/${id}/`, payload)
);
