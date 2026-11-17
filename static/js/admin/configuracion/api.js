import { CONFIG } from '../../shared/core/config.js';
import { getJSON, patchJSON } from '../../shared/core/http.js';

const urlPerfil = () => `${CONFIG.USUARIOS}/admin/perfil/`;

export const obtenerPerfil = () => getJSON(urlPerfil());

export const actualizarPerfil = (payload) => patchJSON(urlPerfil(), payload);
