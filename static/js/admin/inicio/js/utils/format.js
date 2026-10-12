// static/js/admin/inicio/js/utils/format.js
const nf = new Intl.NumberFormat('es-BO');
export const formatearNumero = (n) => nf.format(Number(n) || 0);
