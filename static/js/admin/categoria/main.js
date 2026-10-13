// static/js/admin/categorias/js/main.js
import { 
    getCategorias,
    postCategoria,
    updateCategoria,
    deleteCategoria
} from './api.js';
import { renderTablaCategorias } from './render_tabla.js';
import { agregarFilaCategoria } from './form_categoria.js';

// 1. Cargar la tabla al inicio
const categorias = await getCategorias();
renderTablaCategorias(categorias);

// 2. Escuchar el submit del form
const form = document.getElementById('form-categoria');
const inputNombre = document.getElementById('categoria-nombre');

// 3. Escuchar los botones para EDITAR/ELEMINAR una categoria
const tbody = document.getElementById('tbody-categorias');

// 4. Monitor de informacion de una linea
const label = document.getElementById('categoria-label-status');

// 5. Label de mensaje éxito en el hint
const hint = document.querySelector('.label-hint');

// 6. Variable para cambiar de modos EDITAR/AGREGAR/ELEMINAR
let mode = "AGREGAR";

// 7. el ID para editar o eleminar
let id_categoria = 0;

// Funcion: Para poner texto por defecto en la area del INPUT
function setInputText(texto){
    inputNombre.value = texto;
}

// Funcion: Para cambiar el texto de una etiqueta especifica
function setLabelStatus(texto) {
  if (label) label.textContent = texto;
}

// Funcion: para cambiar el texto del label de que esta arriba del input
function setLabelReport(texto, color = null) {
  hint.textContent = texto;

  if (color) {
    hint.style.color = color;   // color personalizado
  } else {
    hint.style.color = '';      // vuelve al color del CSS (verde)
  }

  hint.classList.add('visible');
}

// Cuando se hace click en guardar para enviar al backend
form?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const nombre = inputNombre.value.trim();
  if (!nombre) return;

  try {
    // --- Caso feliz --- Procediendo con el caso
    const resultado = await procederConModo(mode, {
      id: id_categoria,
      nombre: nombre,
    });

    setLabelReport(resultado.mensaje); 

    // Actualizar la categoria
    const categoria = categorias.find(c => c.id == id_categoria);
    if (categoria) {
      categoria.nombre = inputNombre.value.trim();
    }


    // Actualizar la tabla
    renderTablaCategorias(categorias)
    
  } catch (err) {
    // --- Caso no feliz ---
    console.error(`[main] error al proceder con el modo "${mode}":`, err.message);
    alert(err.message);
  }
});


// Para saber que hacer en los clicks de editar/eleminar de la tabla que esta
// en categoria
tbody?.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-id]');
  if (!btn) return;

  const id = btn.dataset.id;

    if (btn.classList.contains('editar')) {
      console.log('Editar categoría', id);
      setLabelStatus('Editar Categoria');
      id_categoria = id;
      mode = "EDITAR";

      const nombreCategoria = categorias.find(c => c.id == id_categoria)?.nombre ?? null;

      if (nombreCategoria === null) {
        console.warn(`No se encontró categoría con id ${id_categoria}`);
      }

      setInputText(nombreCategoria);
    
    }

    if (btn.classList.contains('eliminar')) {
      console.log('Eliminar categoría', id);
      setLabelStatus('Eliminar Categoria');
      id_categoria = id;
      mode = "ELIMINAR";

      const nombreCategoria = categorias.find(c => c.id == id_categoria)?.nombre ?? null;

      if (nombreCategoria === null) {
        console.warn(`No se encontró categoría con id ${id_categoria}`);
      }

      setInputText(nombreCategoria);
    }
});


/**
 * Ejecuta la acción correspondiente según el modo.
 *
 * @param {'AGREGAR'|'EDITAR'|'ELIMINAR'} mode
 * @param {Object} [data]
 * @param {number} [data.id]      - Requerido en EDITAR y ELIMINAR
 * @param {string} [data.nombre]  - Requerido en AGREGAR y EDITAR
 */
async function procederConModo(mode, data = {}) {
  switch (mode) {
    case 'AGREGAR': {
      if (!data.nombre) throw new Error('Falta el nombre para agregar.');
      const nueva = await postCategoria(data.nombre);
      agregarFilaCategoria(nueva);
      form.reset();

      return { ok: true, mensaje: `fue añadida con éxito.` };
    }

    case 'EDITAR': {
      if (!data.id) throw new Error('Falta el id para editar.');
      if (!data.nombre) throw new Error('Falta el nombre para editar.');
      const actualizada = await updateCategoria(data.id, data.nombre);

      return { ok: true, mensaje: `fue actualizada con éxito.` };
    }

    case 'ELIMINAR': {
      if (!data.id) throw new Error('Falta el id para eliminar.');
      await deleteCategoria(data.id);

      return { ok: true, mensaje: `fue eliminada con éxito.` };
    }

    default:
      console.error('[procederConModo] Modo desconocido:', mode);
      throw new Error(`Modo inválido: "${mode}". Esperado: AGREGAR, EDITAR o ELIMINAR.`);
  }
}


// Para cambiar al modo normal
document.getElementById('btn-guardar-categoria').addEventListener('click', (e) => {
    mode = "AGREGAR"    

    setLabelStatus("Agregar Categoria")
})
