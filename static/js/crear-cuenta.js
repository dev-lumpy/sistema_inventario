/*
=========================================================================
Lógica del registro. Valida los 3 campos (usuario, correo Gmail y
contraseña), muestra fuerza de contraseña en vivo, y deja el fetch
real comentado donde tenés que conectarlo con tu backend.
=========================================================================
*/
const form = document.getElementById('registerForm');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');

const usernameError = document.getElementById('usernameError');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');

const btnRegister = document.getElementById('btnRegister');
const formMsg = document.getElementById('formMsg');
const togglePass = document.getElementById('togglePass');
const strengthBar = document.getElementById('strengthBar');
const strengthLabel = document.getElementById('strengthLabel');

const username_admin = document.getElementById('adminUsername');

let rol = "";

// Mostrar / ocultar contraseña
togglePass.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    togglePass.innerHTML = `<i class="fa-solid ${isPassword ? 'fa-eye-slash' : 'fa-eye'}"></i>`;
});

function showFieldError(input, errorEl, show){
    input.classList.toggle('error', show);
    if (!show) input.classList.add('valid'); else input.classList.remove('valid');
    errorEl.classList.toggle('show', show);
}

function isValidGmail(value){
    return /^[^\s@]+@gmail\.com$/i.test(value.trim());
}

// Fuerza de contraseña en vivo (solo visual, no bloquea el envío)
passwordInput.addEventListener('input', () => {
    const value = passwordInput.value;
    let score = 0;
    if (value.length >= 8) score++;
    if (/[A-Z]/.test(value) && /[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value) && value.length >= 10) score++;

    strengthBar.className = 'strength-bar';
    strengthLabel.className = 'strength-label';

    if (!value){
        strengthLabel.textContent = '';
        return;
    }
    if (score <= 1){
        strengthBar.classList.add('weak');
        strengthLabel.classList.add('weak');
        strengthLabel.textContent = 'Débil';
    } else if (score === 2){
        strengthBar.classList.add('medium');
        strengthLabel.classList.add('medium');
        strengthLabel.textContent = 'Media';
    } else {
        strengthBar.classList.add('strong');
        strengthLabel.classList.add('strong');
        strengthLabel.textContent = 'Fuerte';
    }
});

function setLoading(isLoading){
    btnRegister.classList.toggle('loading', isLoading);
    btnRegister.disabled = isLoading;
}

function showFormMsg(text, type){
    formMsg.textContent = text;
    formMsg.className = `form-msg show ${type}`;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    const usernameOk = username.length >= 3;
    const emailOk = isValidGmail(email);
    const passwordOk = password.length >= 8;

    showFieldError(usernameInput, usernameError, !usernameOk);
    showFieldError(emailInput, emailError, !emailOk);
    showFieldError(passwordInput, passwordError, !passwordOk);

    if (!usernameOk || !emailOk || !passwordOk) return;

    setLoading(true);
    formMsg.classList.remove('show');

    try {

        const res = await fetch('/usuarios/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password, rol, username_admin})
        });
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || errData.email || 'No se pudo crear la cuenta');
        }

        showFormMsg('Cuenta creada correctamente.', 'ok');
        setTimeout(() => { window.location.href = '/'; }, 1500);
    } catch (err) {
        showFormMsg(err.message, 'fail');
    } finally {
        setLoading(false);
    }
});


// Comportamiento de eleccion de ROL
document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll('input[name="rol"]');
    const adminField = document.getElementById('adminField');

    function toggleAdminField() {
        const seleccionado = document.querySelector('input[name="rol"]:checked');
        if (!seleccionado) return;

        if (seleccionado.value === 'administrador') {
            adminField.style.display = 'none';    // ocultar
            rol = seleccionado.value;
            
        } else {
            adminField.style.display = 'block';   // mostrar
            rol = seleccionado.value;
        }
        console.log(rol);
    }

    radios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            toggleAdminField();
        });
    });

});
