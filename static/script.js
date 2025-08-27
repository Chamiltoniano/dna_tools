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

    xhr.onload = () => {
        const response = JSON.parse(xhr.responseText);
        if (xhr.status === 200 && response.success) {
            status.textContent = `File "${response.filename}" uploaded successfully.`;
            fetch(`/uploads/${response.filename}`)
                .then(res => res.text())
                .then(pdbData => {
                    renderMolecule(pdbData, response.filename);
                });
        } else {
            status.textContent = `Upload failed: ${response.error}`;
        }
        progressBar.style.display = 'none';
        progressBar.value = 0;
    };

    xhr.upload.addEventListener('progress', e => {
        progressBar.style.display = 'block';
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.value = percent;
        }
    });

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

    status.textContent = '';

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
    })
    .catch(error => {
        console.error(error);
        status.textContent = '❌ Error during generation.';
        alert("Error: " + error.message);
    });

    closeModal();
}

function renderMolecule(pdbData, filename) {
    const viewerDiv = document.getElementById('viewer3d');
    const scrollY = window.scrollY;

    requestAnimationFrame(() => {
        viewerDiv.style.display = 'block';
        window.scrollTo({ top: scrollY, behavior: 'instant' });

        // Limpia contenido anterior si lo hubiera
        viewerDiv.innerHTML = "";

        const viewer = $3Dmol.createViewer(viewerDiv, {
            backgroundColor: "black"
        });

        viewer.addModel(pdbData, "pdb");

        viewer.setStyle({}, {
            sphere: {
                scale: 0.3,
                colorscheme: atom => {
                    const colorMap = {
                        H: "white",
                        O: "red",
                        C: "black",
                        N: "blue",
                        P: "orange"
                    };
                    return colorMap[atom.elem] || "green";
                }
            }
        });

        viewer.addLabel("X", { position: { x: 20, y: 0, z: 0 }, fontColor: "white" });
        viewer.addLabel("Y", { position: { x: 0, y: 20, z: 0 }, fontColor: "white" });
        viewer.addLabel("Z", { position: { x: 0, y: 0, z: 20 }, fontColor: "white" });

        viewer.zoomTo();
        viewer.render();

        // Fuerza alto y margen para evitar scrolls extra o zonas blancas
        viewerDiv.style.height = "500px";
        viewerDiv.style.marginTop = "30px";


       const out = document.getElementById('rg-output');
       if (out && filename) {
         out.textContent = 'Computing radius of gyration...';
         fetch(`/pcoords/rg/${encodeURIComponent(filename)}`)
           .then(res => res.json())
           .then(data => {
             if (data && data.success) {
               const r = Number(data.r).toFixed(4);
               const cm = (data.CM || [0,0,0]).map(v => Number(v).toFixed(4));
               out.textContent = `Radius of gyration (A): ${r}   |   CM: (${cm[0]}, ${cm[1]}, ${cm[2]})   |   n = ${data.nTotal}`;
             } else {
               out.textContent = 'Could not compute radius of gyration.';
             }
           })
           .catch(() => {
             out.textContent = 'Could not compute radius of gyration.';
           });
       }
    });
}
