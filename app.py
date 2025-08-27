from flask import Flask, request, render_template, jsonify, send_file, send_from_directory
import os
import subprocess
from datetime import datetime
import json
import numpy as np

# Import del extractor (archivo en la raíz del repo)
from pcoords_extraction import extract_and_store_pcoord_sets

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
    """
    Recibe un .pdb, lo guarda en uploads/ y extrae coordenadas de átomos P.
    Guarda un JSON silencioso: uploads/<filename>_P_coords.json con A y B.
    """
    file = request.files.get('file')
    if file and file.filename.endswith('.pdb'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extraer y guardar coordenadas P (silencioso; no interrumpe el flujo si falla)
        try:
            out_json = extract_and_store_pcoord_sets(filepath)
            app.logger.info(f"P coords guardadas en {out_json}")
        except Exception as e:
            app.logger.warning(f"Extracción P falló para {filepath}: {e}")

        return jsonify({'success': True, 'filename': file.filename})
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Permite acceder al archivo .pdb subido desde el frontend para ser renderizado por 3Dmol.js"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/generate', methods=['POST'])
def generate():
    """
    Genera un PDB a partir de secuencia y sigma usando generate_b_dna.py y ordenar_pdb.py.
    Si topology == "circular", intenta circularizar con circularizarDNA.py.
    No ejecuta extracción de P: solo aplica al flujo de subida/visualización.
    """
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
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        details = (e.stderr or b'').decode(errors='ignore')
        return jsonify({'error': 'DNA generation failed', 'details': details}), 500

    # Ejecuta ordenar_pdb.py
    try:
        subprocess.run(['python3', 'ordenar_pdb.py'], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        details = (e.stderr or b'').decode(errors='ignore')
        return jsonify({'error': 'Sorting failed', 'details': details}), 500

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


# ============
# Cálculo de radio de giro (usando la matriz A del JSON de P)
# Tu fórmula de MATLAB: r = sqrt((1/n^2) * sum_{i,j} ||ri - rj||^2) = sqrt(2 * mean(||ri - CM||^2))
# ============

def calc_radius_of_gyration_and_cm_from_A(A_list):
    """
    A_list: lista de [x, y, z] (matriz A).
    Devuelve: (r, CM) donde r es el radio de giro (según tu fórmula en MATLAB)
              y CM es [CMx, CMy, CMz].
    """
    A = np.asarray(A_list, dtype=float)
    nTotal = A.shape[0]
    if nTotal == 0:
        return 0.0, [0.0, 0.0, 0.0]

    # Centro de masa
    CM = A.mean(axis=0)

    # r = sqrt( (1/n^2) * sum_{i,j} ||ri - rj||^2 )
    # Equivalente eficiente: mean_pairwise_sq = 2 * mean(||ri - CM||^2)
    dif = A - CM
    mean_sq_to_CM = np.mean(np.sum(dif * dif, axis=1))
    mean_pairwise_sq = 2.0 * mean_sq_to_CM
    r = float(np.sqrt(mean_pairwise_sq))
    return r, [float(CM[0]), float(CM[1]), float(CM[2])]


@app.route('/pcoords/rg/<filename>', methods=['GET'])
def pcoords_rg(filename):
    """
    Lee uploads/<filename>_P_coords.json, toma la matriz A y devuelve r y CM.
    'filename' debe ser EXACTAMENTE el nombre del .pdb subido (ej: 'miADN.pdb').
    """
    try:
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_P_coords.json")
        if not os.path.exists(json_path):
            return jsonify({'error': f'P-coords JSON not found for {filename}'}), 404

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        A = data.get('A', [])
        if not A:
            return jsonify({'error': 'Matrix A is empty or missing'}), 400

        r, CM = calc_radius_of_gyration_and_cm_from_A(A)
        return jsonify({'success': True, 'r': r, 'CM': CM, 'nTotal': len(A)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
