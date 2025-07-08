# circularizarDNA_v2.py (Python 3)
import math

def circularize_pdb(input_file, output_file="ADN_circularizado.pdb"):
    pi = math.pi
    M = []  # Coordenadas
    lineas_atom = []
    lineas_no_atom = []

    with open(input_file, 'r') as archivo:
        lineas = archivo.readlines()

    for i, linea in enumerate(lineas):
        if linea.startswith("ATOM"):
            x = float(linea[30:38])
            y = float(linea[38:46])
            z = float(linea[46:54])
            M.append([x, y, z])
            lineas_atom.append(linea)
        else:
            lineas_no_atom.append(linea)

    if not M:
        raise ValueError("No valid ATOM lines found")

    z_min = min(M, key=lambda v: v[2])[2]
    z_max = max(M, key=lambda v: v[2])[2]
    delta_z = z_max - z_min
    radio = delta_z / (2 * pi)

    partes_ultima = lineas_atom[-1].split()
    pares_base = int(partes_ultima[5]) // 2
    angulo_total = 0

    nuevas_coords = []
    for i in range(len(M)):
        x, y, z = M[i]
        theta = ((z - z_min) / delta_z) * angulo_total if delta_z != 0 else 0
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x_rot = cos_theta * x - sin_theta * y
        y_rot = sin_theta * x + cos_theta * y
        x_rot_shifted = x_rot - radio
        z_shifted = z - (delta_z / 2)
        nuevas_coords.append([x_rot_shifted, y_rot, z_shifted])

    nuevas_coords2 = []
    for x, y, z in nuevas_coords:
        if z >= 0:
            theta = (1 - 2 * ((delta_z / 2 - z) / delta_z)) * (-pi - (0.45 * pi) / pares_base)
        else:
            theta = (1 - 2 * ((delta_z / 2 + z) / delta_z)) * (pi + (0.45 * pi) / pares_base)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x_rot = cos_theta * x
        z_rot = sin_theta * x
        nuevas_coords2.append([x_rot, y, z_rot])

    nuevas_lineas = []
    for idx, linea in enumerate(lineas_atom):
        coord = nuevas_coords2[idx]
        nueva_linea = "ATOM  {serial:5d} {name:<4} {resName:3} {chainID:1}{resSeq:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {element:>2}\n".format(
            serial=idx + 1,
            name=linea[12:16].strip(),
            resName=linea[17:20].strip(),
            chainID=linea[21].strip(),
            resSeq=int(linea[22:26].strip()),
            x=coord[0],
            y=coord[1],
            z=coord[2],
            element=linea[76:78].strip()
        )
        nuevas_lineas.append(nueva_linea)

    with open(output_file, 'w') as salida:
        salida.writelines(lineas_no_atom + nuevas_lineas)
