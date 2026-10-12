// static/js/admin/categorias/js/form_categoria.js

/**
 * Agrega una fila nueva a la tabla de categorías.
 * @param {{id:number, nombre:string}} categoria
 */
export function agregarFilaCategoria(categoria) {
  const tbody = document.getElementById('tbody-categorias');
  if (!tbody) return;

  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${categoria.nombre}</td>
    <td class="acciones"></td>
  `;
  tbody.appendChild(tr);
}
