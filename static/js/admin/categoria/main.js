// static/js/admin/categorias/js/main.js
import { getCategorias, postCategoria } from './api.js';
import { renderTablaCategorias } from './render_tabla.js';
import { agregarFilaCategoria } from './form_categoria.js';

// 1. Cargar la tabla al inicio
const categorias = await getCategorias();
renderTablaCategorias(categorias);

// 2. Escuchar el submit del form
const form = document.getElementById('form-categoria');
const inputNombre = document.getElementById('categoria-nombre');

form?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const nombre = inputNombre.value.trim();
  if (!nombre) return;

  try {
    // --- Caso feliz ---
    const nueva = await postCategoria(nombre);
    agregarFilaCategoria(nueva);
    form.reset();

    // Mostrar mensaje de éxito en el hint
    const hint = document.querySelector('.label-hint');
    if (hint) {
      hint.textContent = `La categoría "${nueva.nombre}" fue añadida con éxito.`;
      hint.classList.add('visible');
    }
  } catch (err) {
    // --- Caso no feliz ---
    console.error('[main] error al crear categoría:', err.message);
    alert(err.message);
  }
});














