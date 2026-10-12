// static/js/admin/inicio/js/services/inicio.service.js
import { CONFIG } from '../core/config.js';
import { getJSON } from '../core/http.js';

const MOCK = {
  alertas: [
    { id: 1, nombre: 'Aceite 1L', stock: 0, stock_minimo: 10 },
    { id: 2, nombre: 'Arroz 5kg', stock: 3, stock_minimo: 12 },
    { id: 3, nombre: 'Azúcar 1kg', stock: 8, stock_minimo: 10 },
  ],
  resumen: { ventas: 14, entradas: 3 },
};

const simular = (data) => new Promise((r) => setTimeout(() => r(structuredClone(data)), 250));

export function obtenerAlertasStock() {
  return CONFIG.USE_MOCK ? simular(MOCK.alertas) : getJSON(CONFIG.ENDPOINTS.alertasStock);
}

export function obtenerResumenHoy() {
  return CONFIG.USE_MOCK ? simular(MOCK.resumen) : getJSON(CONFIG.ENDPOINTS.resumenHoy);
}
