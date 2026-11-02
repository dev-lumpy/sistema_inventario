export const CONFIG = {
  API_BASE: '/api',
  INVENTARIO: '/api/inventario',
  USUARIOS: '/api/usuarios',
};

export const ENDPOINTS = {
  // Categorías
  categorias: `${CONFIG.INVENTARIO}/categorias/select/`,
  categoriaCreate: `${CONFIG.INVENTARIO}/add_categoria/`,
  categoriaDetail: (id) => `${CONFIG.INVENTARIO}/categorias/${id}/`,

  // Productos
  productos: `${CONFIG.INVENTARIO}/productos/`,
  productosSelect: `${CONFIG.INVENTARIO}/productos/select_all/`,
  productosAlertas: `${CONFIG.INVENTARIO}/productos/alertas/`,
  productoDetail: (id) => `${CONFIG.INVENTARIO}/productos/${id}/`,

  // Proveedores
  proveedoresSelect: `${CONFIG.INVENTARIO}/proveedores/select/`,

  // Movimientos
  resumenHoy: `${CONFIG.INVENTARIO}/resumen/hoy/`,
  entradaStock: `${CONFIG.INVENTARIO}/movimiento/entrada/`,
  entradaHistorial: `${CONFIG.INVENTARIO}/movimiento/entrada/historial/`,
  historialProductos: `${CONFIG.INVENTARIO}/history_productos/`,
  historialMovimientos: `${CONFIG.INVENTARIO}/history_movimientos/`,
};
