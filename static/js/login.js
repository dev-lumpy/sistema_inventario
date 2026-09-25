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
        const res = await fetch('/usuarios/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: correo,
                password: password,
            })
        });
        if (!res.ok) throw new Error('Credenciales inválidas');
        const data = await res.json();
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
        localStorage.setItem('usuario', JSON.stringify(data.usuario));

        showFormMsg('Ingreso correcto, redirigiendo...', 'ok');
        
        window.location.href = '/dashboard';

    } catch (err) {
        showFormMsg('Usuario o contraseña incorrectos.', 'fail');
    } finally {
        setLoading(false);
    }
});

