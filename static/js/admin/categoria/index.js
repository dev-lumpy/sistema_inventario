import { $ } from '../../shared/core/dom.js';
import {
  actualizarCategoria,
  crearCategoria,
  eliminarCategoria,
  getCategorias,
} from './api.js';
import { renderTabla, initTabla } from './tabla.js';
import {
  cargarCategoria,
  getEditandoId,
  initFormulario,
  mostrarEstado,
  resetFormulario,
} from './formulario.js';

export async function initCategoria() {
  if (!document.getElementById('form-categoria')) return;

  let categorias = [];

  async function guardar({ id, nombre }) {
    if (id !== null && id !== undefined) {
      const actualizada = await actualizarCategoria(id, nombre);
      categorias = categorias.map(
        (categoria) => (String(categoria.id) === String(id) ? actualizada : categoria),
      );
      renderTabla(categorias);
      return `Categoría "${actualizada.nombre}" actualizada.`;
    }

    const nueva = await crearCategoria(nombre);
    categorias = [...categorias, nueva];
    renderTabla(categorias);
    return `Categoría "${nueva.nombre}" creada.`;
  }

  function editar(id) {
    const categoria = categorias.find(
      (item) => String(item.id) === String(id),
    );
    if (categoria) cargarCategoria(categoria);
  }

  async function eliminar(id) {
    const categoria = categorias.find(
      (item) => String(item.id) === String(id),
    );
    if (!categoria) return;

    if (!confirm(`¿Eliminar la categoría "${categoria.nombre}"?`)) return;

    try {
      await eliminarCategoria(id);
      categorias = categorias.filter(
        (item) => String(item.id) !== String(id),
      );

      const editando = getEditandoId();
      if (editando !== null && String(editando) === String(id)) resetFormulario();

      renderTabla(categorias);
      mostrarEstado(`Categoría "${categoria.nombre}" eliminada.`);
    } catch (error) {
      mostrarEstado(error.message, { error: true });
    }
  }

  
  initTabla({ onEditar: editar, onEliminar: eliminar });
  initFormulario({ onGuardar: guardar });

  $('#btn-guardar-categoria')?.addEventListener('click', () => {
    resetFormulario();
    $('#categoria-nombre')?.focus();
  });

  try {
    categorias = await getCategorias();
    renderTabla(categorias);
  } catch (error) {
    console.error('[categoria]', error);
    mostrarEstado(`No se pudieron cargar las categorías: ${error.message}`, { error: true });
  }
}
