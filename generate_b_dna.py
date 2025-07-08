# -*- coding: utf-8 -*-
import numpy as np
from math import cos, sin, radians


def read_pdb_template(filename):
    """Lee un archivo PDB y retorna las coordenadas de los átomos por residuo."""
    atoms = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('ATOM'):
                atom_data = {
                    'serial': int(line[6:11].strip()),
                    'name': line[12:16].strip(),
                    'resName': line[17:20].strip(),
                    'chainID': line[21:22].strip(),
                    'resSeq': int(line[22:26].strip()),
                    'x': float(line[30:38].strip()),
                    'y': float(line[38:46].strip()),
                    'z': float(line[46:54].strip()),
                    'element': line[76:78].strip()
                }
                atoms.append(atom_data)
    return atoms

def get_nucleotide_coords(template, chain, res_seq):
    """Extrae coordenadas de un nucleótido específico de una cadena y número de residuo."""
    return [atom for atom in template if atom['chainID'] == chain and atom['resSeq'] == res_seq]

def complementary_base(base):
    """Retorna la base complementaria."""
    pairs = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return pairs[base]

def rotate_z(coords, angle_deg):
    """Rota coordenadas alrededor del eje z por un ángulo en grados."""
    angle_rad = radians(angle_deg)
    rotation_matrix = np.array([
        [cos(angle_rad), -sin(angle_rad), 0],
        [sin(angle_rad), cos(angle_rad), 0],
        [0, 0, 1]
    ])
    new_coords = []
    for atom in coords:
        xyz = np.array([atom['x'], atom['y'], atom['z']])
        rotated_xyz = rotation_matrix.dot(xyz)
        new_atom = atom.copy()
        new_atom['x'], new_atom['y'], new_atom['z'] = rotated_xyz
        new_coords.append(new_atom)
    return new_coords

def translate(coords, dz):
    """Traslada coordenadas en la dirección z."""
    new_coords = []
    for atom in coords:
        new_atom = atom.copy()
        new_atom['z'] += dz
        new_coords.append(new_atom)
    return new_coords

def calculate_distance(atom1, atom2):
    """Calcula la distancia euclidiana entre dos átomos."""
    return np.sqrt(
        (atom1['x'] - atom2['x'])**2 +
        (atom1['y'] - atom2['y'])**2 +
        (atom1['z'] - atom2['z'])**2
    )

def validate_hbonds(chain_a_atoms, chain_b_atoms, base_a, base_b):
    """Valida las distancias de los puentes de hidrógeno."""
    expected_range = (2.8, 3.0)
    if base_a == 'A' and base_b == 'T':
        # A-T: N6-H61...O4, N1...H3-N3
        n6 = next((a for a in chain_a_atoms if a['name'] == 'N6'), None)
        h61 = next((a for a in chain_a_atoms if a['name'] == 'H61'), None)
        o4 = next((a for a in chain_b_atoms if a['name'] == 'O4'), None)
        n1 = next((a for a in chain_a_atoms if a['name'] == 'N1'), None)
        h3 = next((a for a in chain_b_atoms if a['name'] == 'H3'), None)
        n3 = next((a for a in chain_b_atoms if a['name'] == 'N3'), None)
        if h61 and o4:
            dist1 = calculate_distance(h61, o4)
            print(f"A-T H61...O4 distance: {dist1:.2f} Å")
            if not (expected_range[0] <= dist1 <= expected_range[1]):
                print(f"Warning: A-T H61...O4 distance out of range {expected_range}")
        if n1 and h3:
            dist2 = calculate_distance(n1, h3)
            print(f"A-T N1...H3 distance: {dist2:.2f} Å")
            if not (expected_range[0] <= dist2 <= expected_range[1]):
                print(f"Warning: A-T N1...H3 distance out of range {expected_range}")
    elif base_a == 'C' and base_b == 'G':
        # C-G: O6...H41-N4, H1-N1...N3, H22-N2...O2
        o6 = next((a for a in chain_b_atoms if a['name'] == 'O6'), None)
        h41 = next((a for a in chain_a_atoms if a['name'] == 'H41'), None)
        n1 = next((a for a in chain_b_atoms if a['name'] == 'N1'), None)
        h1 = next((a for a in chain_b_atoms if a['name'] == 'H1'), None)
        n3 = next((a for a in chain_a_atoms if a['name'] == 'N3'), None)
        h22 = next((a for a in chain_b_atoms if a['name'] == 'H22'), None)
        o2 = next((a for a in chain_a_atoms if a['name'] == 'O2'), None)
        if h41 and o6:
            dist1 = calculate_distance(h41, o6)
            print(f"C-G H41...O6 distance: {dist1:.2f} Å")
            if not (expected_range[0] <= dist1 <= expected_range[1]):
                print(f"Warning: C-G H41...O6 distance out of range {expected_range}")
        if h1 and n3:
            dist2 = calculate_distance(h1, n3)
            print(f"C-G H1...N3 distance: {dist2:.2f} Å")
            if not (expected_range[0] <= dist2 <= expected_range[1]):
                print(f"Warning: C-G H1...N3 distance out of range {expected_range}")
        if h22 and o2:
            dist3 = calculate_distance(h22, o2)
            print(f"C-G H22...O2 distance: {dist3:.2f} Å")
            if not (expected_range[0] <= dist3 <= expected_range[1]):
                print(f"Warning: C-G H22...O2 distance out of range {expected_range}")

def validate_backbone_connectivity(prev_atoms, curr_atoms):
    """Valida la distancia O3'-P entre residuos consecutivos."""
    o3p = next((a for a in prev_atoms if a['name'] == "O3'"), None)
    p = next((a for a in curr_atoms if a['name'] == 'P'), None)
    if o3p and p:
        dist = calculate_distance(o3p, p)
        print(f"O3'-P distance: {dist:.2f} Å")
        if not (1.5 <= dist <= 1.7):
            print(f"Warning: O3'-P distance out of range (1.5-1.7 Å)")

def write_pdb(atoms, filename):
    """Escribe las coordenadas en un archivo PDB."""
    with open(filename, 'w') as f:
        for atom in atoms:
            f.write(
                f"ATOM  {atom['serial']:5d} {atom['name']:<4} {atom['resName']:3} "
                f"{atom['chainID']:1}{atom['resSeq']:4d}    "
                f"{atom['x']:8.3f}{atom['y']:8.3f}{atom['z']:8.3f}"
                f"  1.00  0.00          {atom['element']:>2}\n"
            )
        f.write("TER\n")

def main():
    # Solicitar secuencia al usuario
    sequence = input("Ingrese la secuencia de ADN (solo A, T, C, G): ").upper()
    if not all(base in 'ATCG' for base in sequence):
        print("Error: La secuencia solo debe contener A, T, C o G.")
        return
    try:
        sigma = float(input("Introduce el valor de sigma: "))
    except ValueError:
        print("sigma debe ser un número.")
        sys.exit()
    longitud = len(sequence)
    Lk0=longitud/10.5
    DLk=sigma*Lk0
    AnguloTotal=DLk*360
    anguloPorBase=AnguloTotal/longitud
    # Cargar plantillas
    templates = {
        'AT': read_pdb_template('AT.pdb'),
        'TA': read_pdb_template('TA.pdb'),
        'CG': read_pdb_template('CG.pdb'),
        'GC': read_pdb_template('GC.pdb')
    }

    # Parámetros de la hélice B
    rise = 3.4
    twist = 34.3+anguloPorBase

    # Inicializar lista de átomos
    all_atoms = []
    atom_serial = 1
    prev_chain_a_atoms = None
    prev_chain_b_atoms = None

    # Construir la doble hélice
    for i, base in enumerate(sequence, start=1):
        # Seleccionar plantilla según la base en la cadena principal
        if base == 'A':
            template = templates['AT']
            res_a, res_b = 1, 36  # DA en A, DT en B
            base_a, base_b = 'DA', 'DT'
        elif base == 'T':
            template = templates['TA']
            res_a, res_b = 1, 36  # DT en A, DA en B
            base_a, base_b = 'DT', 'DA'
        elif base == 'C':
            template = templates['CG']
            res_a, res_b = 1, 36  # DC en A, DG en B
            base_a, base_b = 'DC', 'DG'
        elif base == 'G':
            template = templates['GC']
            res_a, res_b = 1, 36  # DG en A, DC en B
            base_a, base_b = 'DG', 'DC'

        # Extraer coordenadas de los nucleótidos
        chain_a_atoms = get_nucleotide_coords(template, 'A', res_a)
        chain_b_atoms = get_nucleotide_coords(template, 'B', res_b)

        # Aplicar transformaciones geométricas
        dz = (i - 1) * rise
        angle = (i - 1) * twist
        chain_a_atoms = translate(rotate_z(chain_a_atoms, angle), dz)
        chain_b_atoms = translate(rotate_z(chain_b_atoms, angle), dz)

        # Actualizar números de serie y residuos
        for atom in chain_a_atoms:
            atom['serial'] = atom_serial
            atom['resSeq'] = i
            atom['chainID'] = 'A'
            atom['resName'] = base_a
            atom_serial += 1
        for atom in chain_b_atoms:
            atom['serial'] = atom_serial
            atom['resSeq'] = len(sequence) + 1 - i  # Cadena B en orden inverso
            atom['chainID'] = 'B'
            atom['resName'] = base_b
            atom_serial += 1

        # Validar puentes de hidrógeno
        print(f"\nValidating base pair {i} ({base_a} - {base_b}):")
        validate_hbonds(chain_a_atoms, chain_b_atoms, base, complementary_base(base))

        # Validar conectividad del esqueleto
        if prev_chain_a_atoms:
            print(f"Validating backbone connectivity (Chain A, residue {i-1} to {i}):")
            validate_backbone_connectivity(prev_chain_a_atoms, chain_a_atoms)
        if prev_chain_b_atoms:
            print(f"Validating backbone connectivity (Chain B, residue {len(sequence)+2-i} to {len(sequence)+1-i}):")
            validate_backbone_connectivity(chain_b_atoms, prev_chain_b_atoms)  # B en orden inverso

        # Agregar átomos a la lista
        all_atoms.extend(chain_a_atoms)
        all_atoms.extend(chain_b_atoms)

        # Actualizar átomos previos
        prev_chain_a_atoms = chain_a_atoms
        prev_chain_b_atoms = chain_b_atoms

    # Escribir archivo PDB
    write_pdb(all_atoms, 'ADN.pdb')
    print(f"\nDLk: {DLk}")
    print(f"\nAngulo por base: {anguloPorBase}")
    print("\nArchivo ADN.pdb generado exitosamente.")

if __name__ == "__main__":
    main()