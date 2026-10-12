// Si existe en el DOM, le añade el listener
userChip.addEventListener('click', () => {
    console.log('Click en la caja de usuario');

    // Ejemplo 1: redirigir a la página de perfil
    // window.location.href = '/perfil/';

    // Ejemplo 2: abrir un dropdown/menú
    // document.querySelector('.user-menu').classList.toggle('open');

    // Ejemplo 3: fetch a un endpoint (logout, etc.)
    // fetch('/api/logout/', { method: 'POST' })
    //     .then(() => window.location.href = '/login/');
});
