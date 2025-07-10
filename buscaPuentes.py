import math
import json

def distancia(p1, p2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

def parse_pdb(filename):
    atoms = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("ATOM"):
                atom = {
                    'name': line[12:16].strip(),
                    'resName': line[17:20].strip(),
                    'chainID': line[21].strip(),
                    'resSeq': int(line[22:26].strip()),
                    'x': float(line[30:38].strip()),
                    'y': float(line[38:46].strip()),
                    'z': float(line[46:54].strip())
                }
                atoms.append(atom)
    return atoms

def buscar_puentes(atoms):
    res_dict = {}
    for atom in atoms:
        key = (atom['chainID'], atom['resSeq'], atom['resName'])
        if key not in res_dict:
            res_dict[key] = []
        res_dict[key].append(atom)

    res_list = list(res_dict.items())
    n = len(res_list)
    resultados = {
        "pairs": [],
        "bonds": []
    }

    for i in range(n):
        for j in range(i + 1, n):
            key1, atoms1 = res_list[i]
            key2, atoms2 = res_list[j]

            # Solo pares complementarios
            base_set = {key1[2], key2[2]}
            if base_set not in [{"A", "T"}, {"T", "A"}, {"C", "G"}, {"G", "C"}]:
                continue

            dist_min = min(
                distancia((a['x'], a['y'], a['z']), (b['x'], b['y'], b['z']))
                for a in atoms1 for b in atoms2
            )

            hay_enlace = dist_min < 3.5
            resultados["pairs"].append(f"{key1[2]}-{key2[2]}")
            resultados["bonds"].append(1 if hay_enlace else 0)

    return resultados

if __name__ == '__main__':
    atoms = parse_pdb("ADN_ordenado.pdb")
    resultado = buscar_puentes(atoms)
    with open("puentes.json", "w") as f:
        json.dump(resultado, f, indent=2)
    print("Archivo puentes.json generado.")