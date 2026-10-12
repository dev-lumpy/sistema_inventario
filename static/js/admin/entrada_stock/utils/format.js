// static/js/admin/entrada_stock/js/utils/format.js
export function formatearFecha(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function formatearNumero(n) {
  return Number(n).toLocaleString('es-AR');
}
