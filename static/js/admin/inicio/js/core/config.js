// static/js/admin/inicio/js/core/config.js
// Configuración global. Cambia USE_MOCK a false cuando tengas el backend listo.
export const CONFIG = {
  USE_MOCK: false,
  API_BASE: '/api/inventario',
  ENDPOINTS: {
    alertasStock: '/productos/alertas',   // -> [{ id, nombre, stock, stock_minimo }]
    resumenHoy: '/resumen/hoy',           // -> { ventas, entradas }
  },
};
