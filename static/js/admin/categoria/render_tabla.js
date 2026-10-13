// static/js/admin/categorias/js/render_tabla.js

/**
 * Renderiza la tabla de categorías en <tbody id="tbody-categorias">.
 * @param {Array<{id:number, nombre:string}>} categorias
 */
export function renderTablaCategorias(categorias) {
  const tbody = document.getElementById('tbody-categorias');
  if (!tbody) return;

  tbody.replaceChildren();

  if (!categorias || !categorias.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 2;
    td.className = 'empty-state';
    td.textContent = 'No hay categorías registradas.';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  for (const c of categorias) {
    const tr = document.createElement('tr');

    // Columna: Nombre
    const tdNombre = document.createElement('td');
    tdNombre.textContent = c.nombre;

    // Columna: Acciones 
    const tdAcciones = document.createElement('td');
    tdAcciones.className = 'acciones';
    tdAcciones.innerHTML = `
    <button class="btn-icon editar" data-id="${c.id}" title="Editar">
    <i class="fa-solid fa-pen"></i> Editar
    </button>
    `;
    tr.append(tdNombre, tdAcciones);
    tbody.appendChild(tr);
  }
}


