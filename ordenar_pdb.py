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
    return "{:6s}{:5d} {:^4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f} {:8.3f}{:6.2f}{:6.2f}          {:>2s}{:2s}\n".format(
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
    """
    Sorts a PDB file by chain A, then chain B, renumbering atoms.
    """
    atom_records = []
    with open(input_pdb_file, 'r') as infile:
        for line in infile:
            if line.startswith("ATOM"):
                atom_records.append(parse_pdb_line(line))

    df = pd.DataFrame(atom_records)

    # Separate chains
    chain_a = df[df['chain_id'] == 'A'].copy()
    chain_b = df[df['chain_id'] == 'B'].copy()

    # Sort each chain by residue number
    chain_a_sorted = chain_a.sort_values(by='residue_number')
    chain_b_sorted = chain_b.sort_values(by='residue_number')

    # Renumber atoms
    sorted_records = []
    atom_counter = 1
    for index, row in chain_a_sorted.iterrows():
        row_dict = row.to_dict()
        row_dict['atom_number'] = atom_counter
        sorted_records.append(row_dict)
        atom_counter += 1

    # Add TER record after chain A
    ter_record_a = {
        'record_type': 'TER',
        'atom_number': atom_counter,
        'atom_name': '',
        'alt_loc': '',
        'residue_name': chain_a_sorted.iloc[-1]['residue_name'] if not chain_a_sorted.empty else '',
        'chain_id': 'A',
        'residue_number': chain_a_sorted.iloc[-1]['residue_number'] if not chain_a_sorted.empty else 0,
        'insertion_code': '',
        'x_coord': 0.0, # Placeholder, not used for TER
        'y_coord': 0.0, # Placeholder, not used for TER
        'z_coord': 0.0, # Placeholder, not used for TER
        'occupancy': 1.00, # Placeholder
        'temp_factor': 0.00, # Placeholder
        'element_symbol': '', # Placeholder
        'charge': '' # Placeholder
    }
    # Only append TER if chain A had records
    if not chain_a_sorted.empty:
        sorted_records.append(ter_record_a)
        atom_counter +=1


    for index, row in chain_b_sorted.iterrows():
        row_dict = row.to_dict()
        row_dict['atom_number'] = atom_counter
        sorted_records.append(row_dict)
        atom_counter += 1

    # Add TER record after chain B
    ter_record_b = {
        'record_type': 'TER',
        'atom_number': atom_counter,
        'atom_name': '',
        'alt_loc': '',
        'residue_name': chain_b_sorted.iloc[-1]['residue_name'] if not chain_b_sorted.empty else '',
        'chain_id': 'B',
        'residue_number': chain_b_sorted.iloc[-1]['residue_number'] if not chain_b_sorted.empty else 0,
        'insertion_code': '',
        'x_coord': 0.0,
        'y_coord': 0.0,
        'z_coord': 0.0,
        'occupancy': 1.00,
        'temp_factor': 0.00,
        'element_symbol': '',
        'charge': ''
    }
    # Only append TER if chain B had records
    if not chain_b_sorted.empty:
        sorted_records.append(ter_record_b)


    with open(output_pdb_file, 'w') as outfile:
        for record in sorted_records:
            if record['record_type'] == "ATOM":
                outfile.write(format_pdb_line(record))
            elif record['record_type'] == "TER":
                 # Simplified TER record for PDB standard (atom number, residue name, chain ID, residue number)
                outfile.write("TER   {:5d}      {:3s} {:1s}{:4d}\n".format(
                    record['atom_number'],
                    record['residue_name'],
                    record['chain_id'],
                    record['residue_number']
                ))
  #  print(f"Processed PDB file written to {output_pdb_file}")

if __name__ == "__main__":
    # Create a dummy ADN.pdb for testing if it doesn't exist
    try:
        with open("ADN.pdb", "r") as f:
            pass
    except FileNotFoundError:
        print("ADN.pdb not found, creating a dummy file for testing.")
        dummy_pdb_content = """\
ATOM      1 P    DA  A   1       4.728  -7.626   1.239  1.00  0.00           P
ATOM     33 P    DT  B  83      -5.792   6.854   5.521  1.00  0.00           P
ATOM     65 P    DT  A   2       8.307  -3.391   4.639  1.00  0.00           P
ATOM     97 P    DA  B  82      -8.715   2.141   8.921  1.00  0.00           P
"""
        with open("ADN.pdb", "w") as f:
            f.write(dummy_pdb_content)

    sort_pdb()
