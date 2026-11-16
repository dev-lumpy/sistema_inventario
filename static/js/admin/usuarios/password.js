export function esPasswordValida(password) {
  if (password.length < 8) return false;
  if (!/[A-Z]/.test(password)) return false;
  if (!/[a-z]/.test(password)) return false;
  if (!/\d/.test(password)) return false;
  if (!/[!@#$%^&*()_\-+=]/.test(password)) return false;
  if (/\s/.test(password)) return false;
  if (/(.)\1{3,}/.test(password)) return false;

  const bajo = password.toLowerCase();
  for (const secuencia of ['0123456789', 'abcdefghijklmnopqrstuvwxyz']) {
    for (let i = 0; i <= secuencia.length - 4; i += 1) {
      if (bajo.includes(secuencia.slice(i, i + 4))) return false;
    }
  }

  return true;
}

export function generarPasswordTemporal() {
  const mayusculas = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  const minusculas = 'abcdefghijkmnopqrstuvwxyz';
  const digitos = '23456789';
  const especiales = '!@#$%^&*';
  const todos = mayusculas + minusculas + digitos + especiales;
  const elegir = (conjunto) => conjunto[Math.floor(Math.random() * conjunto.length)];

  for (let intento = 0; intento < 20; intento += 1) {
    let password = elegir(mayusculas) + elegir(minusculas) + elegir(digitos) + elegir(especiales);
    while (password.length < 12) password += elegir(todos);
    if (esPasswordValida(password)) return password;
  }

  return 'Taller#2026';
}
