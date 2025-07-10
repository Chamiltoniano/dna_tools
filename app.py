from flask import Flask, request, render_template, jsonify, send_file, send_from_directory
import os
import subprocess
from datetime import datetime
import json

# Intentamos importar la función de circularización si existe
try:
    from circularizarDNA import circularize_pdb
except ImportError:
    circularize_pdb = None

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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Permite acceder al archivo .pdb subido desde el frontend para ser renderizado por 3Dmol.js"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    sequence = data.get('sequence', '').upper()
    sigma = data.get('sigma')
    topology = data.get('topology', 'linear')

    # Validaciones
    if not sequence or not all(base in 'ATCG' for base in sequence):
        return jsonify({'error': 'Invalid DNA sequence'}), 400
    try:
        sigma = float(sigma)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid sigma value'}), 400

    # Simula input para generate_b_dna.py
    temp_input = f"{sequence}\n{sigma}\n"

    try:
        subprocess.run(
            ['python3', 'generate_b_dna.py'],
            input=temp_input.encode(),
            check=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'DNA generation failed', 'details': e.stderr.decode()}), 500

    # Ejecuta ordenar_pdb.py
    try:
        subprocess.run(['python3', 'ordenar_pdb.py'], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Sorting failed', 'details': e.stderr.decode()}), 500

    # Ejecuta buscaPuentes.py
    try:
        subprocess.run(['python3', 'buscaPuentes.py'], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'H-bond detection failed', 'details': e.stderr.decode()}), 500

    # Renombra salida ordenada
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"ADN_{timestamp}.pdb"
    os.rename("ADN_ordenado.pdb", output_name)

    # Circulariza si corresponde
    if topology == "circular":
        if circularize_pdb is None:
            return jsonify({'error': 'Circularization script not available'}), 500
        try:
            circularize_pdb(output_name, output_name)  # sobrescribe el archivo
        except Exception as e:
            return jsonify({'error': 'Circularization failed', 'details': str(e)}), 500

    return send_file(output_name, as_attachment=True)

@app.route('/hbond-data')
def hbond_data():
    try:
        with open('puentes.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Cannot read hbond data', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
