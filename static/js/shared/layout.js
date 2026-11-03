import { $, $$ } from './core/dom.js';
import { initRouter } from './core/router.js';

function initSidebar() {
  $$('.sidebarToggle').forEach((boton) => {
    boton.addEventListener('click', () => {
      $('#sidebar')?.classList.toggle('open');
    });
  });
}

function initUserMenu() {
  const chip = $('#userChip');
  const dropdown = $('#userDropdown');
  if (!chip || !dropdown) return;

  chip.addEventListener('click', (evento) => {
    evento.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') dropdown.classList.remove('open');
  });
}

function initLogout() {
  const boton = $('#btnLogout');
  if (!boton) return;

  boton.addEventListener('click', async () => {
    try {
      await fetch('/api/usuarios/auth/logout/', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      window.location.href = '/login/';
    }
  });
}

initRouter();
initSidebar();
initUserMenu();
initLogout();
