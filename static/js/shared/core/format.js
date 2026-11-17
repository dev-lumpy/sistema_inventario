const numeroBO = new Intl.NumberFormat('es-BO');
const monedaActual = (
  typeof window !== 'undefined' && window.APP_MONEDA
) ? window.APP_MONEDA : 'BOB';

let monedaBO;
try {
  monedaBO = new Intl.NumberFormat('es-BO', {
    style: 'currency',
    currency: monedaActual,
  });
} catch {
  monedaBO = new Intl.NumberFormat('es-BO', {
    style: 'currency',
    currency: 'BOB',
  });
}

export const formatearNumero = (valor) => numeroBO.format(Number(valor) || 0);

const formatosMoneda = new Map();

function formatoPara(moneda) {
  const codigo = String(moneda || monedaActual).toUpperCase();
  if (formatosMoneda.has(codigo)) return formatosMoneda.get(codigo);

  let formato;
  try {
    formato = new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: codigo,
    });
  } catch {
    formato = monedaBO;
  }
  formatosMoneda.set(codigo, formato);
  return formato;
}

export const formatearPrecio = (valor, moneda) => (
  formatoPara(moneda).format(Number(valor) || 0)
);

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
