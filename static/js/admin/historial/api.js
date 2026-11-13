import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON } from '../../shared/core/http.js';

export const LIMITE_MOVIMIENTOS = 100;

export const getMovimientos = (limite = LIMITE_MOVIMIENTOS) => (
  getJSON(`${ENDPOINTS.historialMovimientos}${limite}/`)
);

