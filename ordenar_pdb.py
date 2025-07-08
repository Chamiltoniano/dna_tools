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
    Sorts a PDB file by chain A then B, and by residue number, but preserves atom order within residues.
    """
    atom_records = []
    with open(input_pdb_file, 'r') as infile:
        for line in infile:
            if line.startswith("ATOM"):
                atom_records.append(parse_pdb_line(line))

    df = pd.DataFrame(atom_records)

    # Orden jerárquico: primero cadena, luego número de residuo, luego número original
    df['original_order'] = range(len(df))
    df_sorted = df.sort_values(by=['chain_id', 'residue_number', 'original_order'])

    # Renumerar átomos
    df_sorted = df_sorted.reset_index(drop=True)
    df_sorted['atom_number'] = df_sorted.index + 1

    with open(output_pdb_file, 'w') as outfile:
        last_chain = None
        for _, row in df_sorted.iterrows():
            if last_chain and row['chain_id'] != last_chain:
                # Insertar TER entre cadenas
                ter_line = "TER   {:5d}      {:3s} {:1s}{:4d}\n".format(
                    row['atom_number'],
                    row['residue_name'],
                    last_chain,
                    row['residue_number'] - 1
                )
                outfile.write(ter_line)
            outfile.write(format_pdb_line(row.to_dict()))
            last_chain = row['chain_id']

        # TER final
        if last_chain:
            last_res = df_sorted[df_sorted['chain_id'] == last_chain].iloc[-1]
            outfile.write("TER   {:5d}      {:3s} {:1s}{:4d}\n".format(
                last_res['atom_number'] + 1,
                last_res['residue_name'],
                last_res['chain_id'],
                last_res['residue_number']
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
