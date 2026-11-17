import { initInicio } from './inicio/index.js';
import { initInventario } from './inventario/index.js'
import { initSolicitudes } from './solicitudes/index.js';
import { initVentas } from '../shared/ventas/index.js';

initInicio();
initVentas();
initInventario();
initSolicitudes();
