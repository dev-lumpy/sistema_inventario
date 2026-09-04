let visible = true;

// Hacer aparecer y desaparecer el body
document.addEventListener('DOMContentLoaded', function() {
    const boton = document.querySelector('.btn');
    const tarjeta = document.querySelector('.license-card');
    
    boton.addEventListener('click', function(event) {
        event.preventDefault();
        visibilidad_body(visible, tarjeta)
    });
});

function visibilidad_body(visible, tarjeta){
     // Alternar visibilidad
    if (visible) {
        tarjeta.style.display = 'none';
        console.log('Tarjeta ocultada');
    } else {
        tarjeta.style.display = 'block';
        console.log('Tarjeta mostrada');
    }
    visible = !visible;
}

// Función asíncrona que espera el archivo .lic
async function hacerPeticion() {
    const uploadCard = document.getElementById('uploadCard');
    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('dropzoneInput');
    const filenameText = document.getElementById('dropzoneFilenameText');
    const removeBtn = document.getElementById('dropzoneRemove');

    let selectedFile = null;

    const acceptedTypes = uploadCard.dataset.accept
        ? uploadCard.dataset.accept.split(',').map(t => t.trim().toLowerCase())
        : null;
    const maxMb = parseFloat(uploadCard.dataset.maxMb || '0');


    // Filtra el explorador nativo para que solo muestre los tipos aceptados.
    if (acceptedTypes) input.accept = acceptedTypes.join(',');

    function isValidFile(file){
        if (acceptedTypes){
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!acceptedTypes.includes(ext)) {
                showAlert("error", "Error", `Tipo de archivo no permitido. Solo se acepta: ${acceptedTypes.join(', ')}`, 5000)
                return false;
            }
        }
        if (maxMb > 0 && file.size > maxMb * 1024 * 1024) {
            showAlert("error", "Error", `El archivo supera el límite de ${maxMb} MB.`)
            return false;
        }
        return true;
    }


    function setFile(file){
        if (!isValidFile(file)) return;
        selectedFile = file;
        filenameText.textContent = file.name;
        uploadCard.classList.add('has-file');

        // ---- Acá enganchás tu subida real, por ejemplo: ----
        // const formData = new FormData();
        // formData.append('licencia', selectedFile);
        // fetch('/api/licencia/subir', { method: 'POST', body: formData });
    }

    function clearFile(e){
        e.stopPropagation();
        selectedFile = null;
        input.value = '';
        uploadCard.classList.remove('has-file');
    }

    dropzone.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
        if (input.files.length) setFile(input.files[0]);
    });

    ['dragenter', 'dragover'].forEach(evt =>
        dropzone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        })
    );

    ['dragleave', 'drop'].forEach(evt =>
        dropzone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        })
    );

    dropzone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) setFile(file);
    });

    removeBtn.addEventListener('click', clearFile);

}
