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
    const sequence = document.getElementById('sequenceInput').value.trim();
    if (!sequence) {
        alert("Please enter a sequence.");
        return;
    }

    // Aquí podrías hacer una petición AJAX al backend con la secuencia
    console.log("Sequence submitted:", sequence);

    closeModal();
}
