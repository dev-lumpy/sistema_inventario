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
            body: JSON.stringify({ email: correo, password: password }),
        });

        if (!res.ok) {
            // Leemos el body una sola vez (detail + code del backend)
            const data = await res.json().catch(() => null);
            const detail = data?.detail || null;
            const code = data?.code || null;

            // Mantenemos los strings que tu switch espera
            let msg;
            if (res.status === 400 || res.status === 401) msg = 'INVALID_CREDENTIALS';
            else if (res.status === 403) msg = 'FORBIDDEN';
            else if (res.status === 404) msg = 'NOT_FOUND';
            else if (res.status >= 500) msg = 'SERVER_ERROR';
            else msg = 'UNKNOWN_ERROR';

            const err = new Error(msg);
            err.status = res.status;
            err.detail = detail;
            err.code = code;    
            throw err;
        }

        await res.json();
        showFormMsg('Ingreso correcto, redirigiendo...', 'ok');
        window.location.href = '/dashboard';

    } catch (err) {
        switch (err.message) {
            case 'SERVER_ERROR':
                console.error('Error 500:', err);
                showFormMsg('Hubo un error en el servidor. Intenta más tarde.', 'fail');
                break;
            case 'INVALID_CREDENTIALS':
                // si el backend mandó un detail (cuenta inactiva/pendiente), lo mostramos
                console.error('Error 400/401:', err);
                showFormMsg(err.detail || 'Usuario o contraseña incorrectos.', 'fail');
                break;
            case 'FORBIDDEN':
                console.error('Error 403:', err);
                showFormMsg(err.detail || 'No tienes permisos para acceder.', 'fail');
                break;
            case 'NOT_FOUND':
                console.error('Error 404:', err);
                showFormMsg('El servicio de autenticación no está disponible.', 'fail');
                break;
            default:
                console.error('Error inesperado:', err);
                showFormMsg(err.detail || 'Error de conexión. Verifica tu red.', 'fail');
                break;
        }
    } finally {
        setLoading(false);
    }
});

