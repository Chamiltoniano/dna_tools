from flask import Flask, request, render_template, jsonify, send_file
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.pdb'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': file.filename})
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    sequence = data.get('sequence', '').upper()
    sigma = data.get('sigma')

    # Validaciones
    if not sequence or not all(base in 'ATCG' for base in sequence):
        return jsonify({'error': 'Invalid DNA sequence'}), 400
    try:
        sigma = float(sigma)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid sigma value'}), 400

    # Crear input simulado
    temp_input = f"{sequence}\n{sigma}\n"

    # Ejecutar generate_b_dna.py
    try:
        subprocess.run(
            ['python3', 'generate_b_dna.py'],
            input=temp_input.encode(),
            check=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'DNA generation failed', 'details': e.stderr.decode()}), 500

    # Ejecutar ordenar_pdb.py
    try:
        subprocess.run(['python3', 'ordenar_pdb.py'], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Sorting failed', 'details': e.stderr.decode()}), 500

    # Renombrar archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"ADN_{timestamp}.pdb"
    os.rename("ADN_ordenado.pdb", output_name)

    # Enviar archivo
    return send_file(output_name, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
