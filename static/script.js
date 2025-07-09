const dropArea = document.getElementById('drop-area');
const progressBar = document.getElementById('progress-bar');
const status = document.getElementById('status');
const fileInput = document.getElementById('fileElem');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropArea.addEventListener(event, e => e.preventDefault());
});

dropArea.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    handleFile(file);
});

function handleFile(file) {
    if (!file || !file.name.endsWith('.pdb')) {
        status.textContent = "Please upload a valid .pdb file.";
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload');

    xhr.upload.addEventListener('progress', e => {
        progressBar.style.display = 'block';
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.value = percent;
        }
    });

    xhr.onload = () => {
        const response = JSON.parse(xhr.responseText);
        if (xhr.status === 200 && response.success) {
            status.textContent = `File "${response.filename}" uploaded successfully.`;
        } else {
            status.textContent = `Upload failed: ${response.error}`;
        }
        progressBar.style.display = 'none';
        progressBar.value = 0;
    };

    xhr.send(formData);
}


function openModal() {
    document.getElementById('sequenceModal').classList.add('is-active');
}

function closeModal() {
    document.getElementById('sequenceModal').classList.remove('is-active');
}

function submitSequence() {
    const sequence = document.getElementById('sequenceInput').value.trim().toUpperCase();
    const sigma = parseFloat(document.getElementById('sigmaInput').value);
    const topology = document.querySelector('input[name="topology"]:checked').value;
    const status = document.getElementById('generationStatus');
    const img = document.getElementById('resultImage');

    status.textContent = ''; // reset status

    if (!sequence || !/^[ATCG]+$/.test(sequence)) {
        alert("Please enter a valid DNA sequence (A, T, C, G only).");
        return;
    }

    if (isNaN(sigma)) {
        alert("Please enter a valid number for supercoiling density.");
        return;
    }

    status.textContent = 'Generating...';

    fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence, sigma, topology })
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to generate PDB.");
        return response.blob();
    })
    .then(blob => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ADN_${timestamp}.pdb`;
        document.body.appendChild(a);
        a.click();
        a.remove();

        status.textContent = 'Download ready ✔';
        // Mostrar imagen si deseás en el futuro
        // img.src = 'ruta/a/imagen.png';
        // img.style.display = 'block';
    })
    .catch(error => {
        console.error(error);
        status.textContent = '❌ Error during generation.';
        alert("Error: " + error.message);
    });

    closeModal();
}