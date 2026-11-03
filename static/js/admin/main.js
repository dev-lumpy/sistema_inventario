import { initProductos } from './productos/index.js';
import { initInicio } from './inicio/index.js';
import { initEntradaStock } from './entrada_stock/index.js';
import { initHistorial } from './historial/index.js';
import { initCategoria } from './categoria/index.js';
import { initUsuarios } from './usuarios/index.js';
import { initReporte } from './reporte/index.js';
import { initVentas } from '../shared/ventas/index.js';

initProductos();
initInicio();
initEntradaStock();
initHistorial();
initCategoria();
initUsuarios();
initReporte();
initVentas();
