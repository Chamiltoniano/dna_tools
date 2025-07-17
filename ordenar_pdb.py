import pandas as pd

def parse_pdb_line(line):
    """Parses a PDB ATOM line into a dictionary."""
    record = {}
    record['record_type'] = line[0:6].strip()
    record['atom_number'] = int(line[6:11].strip())
    record['atom_name'] = line[12:16].strip()
    record['alt_loc'] = line[16].strip()
    record['residue_name'] = line[17:20].strip()
    record['chain_id'] = line[21].strip()
    record['residue_number'] = int(line[22:26].strip())
    record['insertion_code'] = line[26].strip()
    record['x_coord'] = float(line[30:38].strip())
    record['y_coord'] = float(line[38:46].strip())
    record['z_coord'] = float(line[46:54].strip())
    record['occupancy'] = float(line[54:60].strip())
    record['temp_factor'] = float(line[60:66].strip())
    record['element_symbol'] = line[76:78].strip()
    record['charge'] = line[78:80].strip()
    return record

def format_pdb_line(record):
    """Formats a PDB ATOM record dictionary back into a PDB line."""
    return "{:6s}{:5d} {:^4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:>2s}{:2s}\n".format(
        record['record_type'],
        record['atom_number'],
        record['atom_name'],
        record['alt_loc'],
        record['residue_name'],
        record['chain_id'],
        record['residue_number'],
        record['insertion_code'],
        record['x_coord'],
        record['y_coord'],
        record['z_coord'],
        record['occupancy'],
        record['temp_factor'],
        record['element_symbol'],
        record['charge']
    )

def sort_pdb(input_pdb_file="ADN.pdb", output_pdb_file="ADN_ordenado.pdb"):
    atom_records = []
    with open(input_pdb_file, 'r') as infile:
        for line in infile:
            if line.startswith("ATOM"):
                atom_records.append(parse_pdb_line(line))

    df = pd.DataFrame(atom_records)

    # Separar las cadenas
    chain_a = df[df['chain_id'] == 'A'].copy()
    chain_b = df[df['chain_id'] == 'B'].copy()

    # Ordenar cada una por número de residuo
    chain_a_sorted = chain_a.sort_values(by='residue_number')
    chain_b_sorted = chain_b.sort_values(by='residue_number')

    # Calcular el offset para la cadena B
    max_resid_a = chain_a_sorted['residue_number'].max() if not chain_a_sorted.empty else 0
    chain_b_sorted['residue_number'] += max_resid_a

    # Renumerar los átomos
    sorted_records = []
    atom_counter = 1
    for _, row in chain_a_sorted.iterrows():
        row_dict = row.to_dict()
        row_dict['atom_number'] = atom_counter
        sorted_records.append(row_dict)
        atom_counter += 1

    # TER después de A
    if not chain_a_sorted.empty:
        sorted_records.append({
            'record_type': 'TER',
            'atom_number': atom_counter,
            'atom_name': '',
            'alt_loc': '',
            'residue_name': chain_a_sorted.iloc[-1]['residue_name'],
            'chain_id': 'A',
            'residue_number': chain_a_sorted.iloc[-1]['residue_number'],
            'insertion_code': '',
            'x_coord': 0.0,
            'y_coord': 0.0,
            'z_coord': 0.0,
            'occupancy': 1.00,
            'temp_factor': 0.00,
            'element_symbol': '',
            'charge': ''
        })
        atom_counter += 1

    for _, row in chain_b_sorted.iterrows():
        row_dict = row.to_dict()
        row_dict['atom_number'] = atom_counter
        sorted_records.append(row_dict)
        atom_counter += 1

    # TER después de B
    if not chain_b_sorted.empty:
        sorted_records.append({
            'record_type': 'TER',
            'atom_number': atom_counter,
            'atom_name': '',
            'alt_loc': '',
            'residue_name': chain_b_sorted.iloc[-1]['residue_name'],
            'chain_id': 'B',
            'residue_number': chain_b_sorted.iloc[-1]['residue_number'],
            'insertion_code': '',
            'x_coord': 0.0,
            'y_coord': 0.0,
            'z_coord': 0.0,
            'occupancy': 1.00,
            'temp_factor': 0.00,
            'element_symbol': '',
            'charge': ''
        })

    with open(output_pdb_file, 'w') as outfile:
        for record in sorted_records:
            if record['record_type'] == "ATOM":
                outfile.write(format_pdb_line(record))
            elif record['record_type'] == "TER":
                outfile.write("TER   {:5d}      {:3s} {:1s}{:4d}\n".format(
                    record['atom_number'],
                    record['residue_name'],
                    record['chain_id'],
                    record['residue_number']
                ))

if __name__ == "__main__":
    sort_pdb()
