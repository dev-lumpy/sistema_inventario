const numeroBO = new Intl.NumberFormat('es-BO');
const monedaBO = new Intl.NumberFormat('es-BO', {
  style: 'currency',
  currency: 'BOB',
});

export const formatearNumero = (valor) => numeroBO.format(Number(valor) || 0);

export const formatearPrecio = (valor) => monedaBO.format(Number(valor) || 0);

export function formatearFecha(iso) {
  if (!iso) return '—';

  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return '—';

  return fecha.toLocaleString('es-BO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
