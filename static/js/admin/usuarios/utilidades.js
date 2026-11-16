export function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

export function idDelUsuarioActual() {
  return document.body.dataset.userId || '';
}

export function nombreAdminActual() {
  return document.getElementById('usuarios')?.dataset.userName || '';
}
