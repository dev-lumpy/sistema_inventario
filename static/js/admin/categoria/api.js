import { ENDPOINTS } from '../../shared/core/config.js';
import { deleteJSON, getJSON, postJSON, putJSON } from '../../shared/core/http.js';

export const getCategorias = () => getJSON(ENDPOINTS.categorias);

export const crearCategoria = (nombre) => postJSON(ENDPOINTS.categoriaCreate, { nombre });

export const actualizarCategoria = (id, nombre) => putJSON(
  ENDPOINTS.categoriaDetail(id),
  { nombre },
);

export const eliminarCategoria = (id) => deleteJSON(ENDPOINTS.categoriaDetail(id));
