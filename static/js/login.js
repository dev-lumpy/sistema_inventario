/*
=========================================================================
Lógica del login. Valida que los campos no estén vacíos, muestra
estado de carga en el botón, y deja el fetch real comentado justo
donde tenés que conectarlo con tu backend.
=========================================================================
*/
const form = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const usernameError = document.getElementById('usernameError');
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

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    showFieldError(usernameInput, usernameError, !username);
    showFieldError(passwordInput, passwordError, !password);

    if (!username || !password) return;

    setLoading(true);
    formMsg.classList.remove('show');

    try {
        // --- Reemplazá este bloque simulado por tu llamada real ---
        await new Promise(resolve => setTimeout(resolve, 1200));
        // const res = await fetch('/api/login', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({
        //     username,
        //     password,
        //     remember: document.getElementById('remember').checked
        //   })
        // });
        // if (!res.ok) throw new Error('Credenciales inválidas');
        // -----------------------------------------------------------

        showFormMsg('Ingreso correcto, redirigiendo...', 'ok');
        // window.location.href = '/dashboard';
    } catch (err) {
        showFormMsg('Usuario o contraseña incorrectos.', 'fail');
    } finally {
        setLoading(false);
    }
});

