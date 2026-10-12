/*
=========================================================================
Lógica del login. Valida que los campos no estén vacíos, muestra
estado de carga en el botón, y deja el fetch real comentado justo
donde tenés que conectarlo con tu backend.
=========================================================================
*/
const form = document.getElementById('loginForm');
const correoInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const correoError = document.getElementById('correoError');
const passwordError = document.getElementById('passwordError');
const btnLogin = document.getElementById('btnLogin');
const formMsg = document.getElementById('formMsg');
const togglePass = document.getElementById('togglePass');

// Mostrar / ocultar contraseña
togglePass.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    togglePass.innerHTML = `<i class="fa-solid ${isPassword ? 'fa-eye-slash' : 'fa-eye'}"></i>`;
});

function showFieldError(input, errorEl, show){
    input.classList.toggle('error', show);
    errorEl.classList.toggle('show', show);
}

function showFormMsg(text, type){
    formMsg.textContent = text;
    formMsg.className = `form-msg show ${type}`;
}

function setLoading(isLoading){
    btnLogin.classList.toggle('loading', isLoading);
    btnLogin.disabled = isLoading;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const correo = correoInput.value.trim();
    const password = passwordInput.value.trim();

    showFieldError(correoInput, correoError, !correo);
    showFieldError(passwordInput, passwordError, !password);

    if (!correo || !password) return;

    setLoading(true);
    formMsg.classList.remove('show');

    try {
        const res = await fetch('/api/usuarios/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: correo,
                password: password,
            })
        });

        // Manejo de errores según el código de estado
        if (!res.ok) {
            if (res.status === 500) {
                throw new Error('SERVER_ERROR');
            } else if (res.status === 401 || res.status === 400) {
                throw new Error('INVALID_CREDENTIALS');
            } else if (res.status === 403) {
                throw new Error('FORBIDDEN');
            } else if (res.status === 404) {
                throw new Error('NOT_FOUND');
            } else if (res.status >= 500) {
                throw new Error('SERVER_ERROR');
            } else {
                throw new Error('UNKNOWN_ERROR');
            }
        }

        const data = await res.json();
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
        localStorage.setItem('usuario', JSON.stringify(data.usuario));

        showFormMsg('Ingreso correcto, redirigiendo...', 'ok');
        
        window.location.href = '/dashboard';

    } catch (err) {
        // Manejo de errores según el tipo
        switch (err.message) {
            case 'SERVER_ERROR':
                console.error('Error 500: Error interno del servidor', err);
                showFormMsg('Hubo un error en el servidor. Por favor, intenta más tarde.', 'fail');
                break;
            case 'INVALID_CREDENTIALS':
                console.error('Error 400/401: Credenciales inválidas', err);
                showFormMsg('Usuario o contraseña incorrectos.', 'fail');
                break;
            case 'FORBIDDEN':
                console.error('Error 403: Acceso prohibido', err);
                showFormMsg('No tienes permisos para acceder.', 'fail');
                break;
            case 'NOT_FOUND':
                console.error('Error 404: Recurso no encontrado', err);
                showFormMsg('El servicio de autenticación no está disponible.', 'fail');
                break;
            default:
                // Errores de red, JSON parse, etc.
                console.error('Error inesperado:', err);
                showFormMsg('Error de conexión. Verifica tu red e intenta de nuevo.', 'fail');
                break;
        }
    } finally {
        setLoading(false);
    }
});

