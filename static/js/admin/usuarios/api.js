import { CONFIG } from '../../shared/core/config.js';
import { postJSON } from '../../shared/core/http.js';

export const crearVendedor = (payload) => (
  postJSON(`${CONFIG.USUARIOS}/registrar-vendedor/`, payload)
);
