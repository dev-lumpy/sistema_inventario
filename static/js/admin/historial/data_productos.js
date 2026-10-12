 // static/js/admin/historial/data_historial.js
//
export function renderHistorialProductos(list_productos) {
  const select = document.getElementById('historial-producto');
  if (!select) return;

  // Limpiar el select dejando solo el placeholder
  select.replaceChildren();
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccioná un producto';
  select.appendChild(placeholder);

  // Productos ordenados alfabéticamente por nombre
  const productos = [...(list_productos || [])].sort((a, b) =>
    a.nombre.localeCompare(b.nombre),
  );

  for (const p of productos) {
    const option = document.createElement('option');
    option.value = p.id;         // ← usamos id, es más robusto
    option.textContent = p.nombre;
    select.appendChild(option);
  }

  select.disabled = productos.length === 0;
} 
