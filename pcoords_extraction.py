"""
Utilidad para extraer coordenadas de átomos de Fósforo (P) desde un PDB,
partirlas en dos mitades (A y B) y guardarlas en un JSON junto al archivo.

No realiza ningún cálculo adicional con las coordenadas.

Uso CLI:
    python pcoords_extraction.py ruta/al/archivo.pdb

Integración Flask (ver al final del archivo):
    from utils.pcoords_extraction import extract_and_store_pcoord_sets
    out_json = extract_and_store_pcoord_sets(pdb_path)
"""
from __future__ import annotations
import os
import json
import re
from typing import List, Tuple


def get_p_coords_from_pdb(pdb_path: str) -> List[List[float]]:
    """Devuelve lista de [x, y, z] para cada átomo de fósforo (P) en un PDB.

    Reglas:
    - Acepta líneas que comiencen con ATOM o HETATM.
    - Intenta detectar el elemento por la columna 77-78 del formato PDB estándar.
      Si está vacío, infiere el elemento de 'atom name'.
    - Considera P cuando element == 'P' o atom name == 'P'.
    - Ignora líneas mal formateadas.
    """
    coords: List[List[float]] = []
    with open(pdb_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not (line.startswith('ATOM') or line.startswith('HETATM')):
                continue
            # Aseguramos longitud para cortes por columnas
            if len(line) < 54:
                continue
            name = line[12:16].strip()
            element = line[76:78].strip() if len(line) >= 78 else ''
            if not element:
                # Fallback: primer carácter alfabético de name
                name_alpha = re.sub(r'[^A-Za-z]', '', name)
                element = name_alpha[:1].upper() if name_alpha else ''
            if element == 'P' or name == 'P':
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                except ValueError:
                    continue
                coords.append([x, y, z])
    return coords


essential_msg = (
    "El número total de coordenadas de P debe ser par. Si no lo es, se descarta "
    "la última coordenada para forzar paridad."
)


def split_even_coords(coords: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """Parte la lista en dos mitades A y B. Si la cantidad es impar, descarta una.
    """
    n = len(coords)
    if n == 0:
        return [], []
    if n % 2 != 0:
        # Forzamos paridad descartando la última entrada
        coords = coords[:-1]
        n -= 1
    mid = n // 2
    A = coords[:mid]
    B = coords[mid:]
    return A, B


def save_pcoord_sets_json(base_path_no_ext: str, A: List[List[float]], B: List[List[float]]) -> str:
    """Guarda A y B en JSON con metadatos simples.

    Crea un archivo "<base>_P_coords.json" en el mismo directorio del PDB.
    Devuelve la ruta del JSON creado.
    """
    out_path = base_path_no_ext + "_P_coords.json"
    data = {
        "A": A,
        "B": B,
        "n_total": len(A) + len(B),
        "nota": "Sin cálculos adicionales; listo para usar luego.",
    }
    with open(out_path, 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    return out_path


def extract_and_store_pcoord_sets(pdb_path: str) -> str:
    """Extrae coordenadas P de un PDB, las divide en A/B y las guarda en JSON.

    Devuelve la ruta del JSON generado.
    """
    coords = get_p_coords_from_pdb(pdb_path)
    A, B = split_even_coords(coords)
    base_no_ext, _ = os.path.splitext(pdb_path)
    out_json = save_pcoord_sets_json(base_no_ext, A, B)
    return out_json


# =============================
# Uso por línea de comando (opcional)
# =============================
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python pcoords_extraction.py ruta/al/archivo.pdb")
        raise SystemExit(1)
    pdb_path_cli = sys.argv[1]
    out = extract_and_store_pcoord_sets(pdb_path_cli)
    print(f"Guardado: {out}")


# =============================
# INTEGRACIÓN FLASK (ejemplo)
# =============================
# Dentro de tu vista que maneja la subida de PDB (después de guardar el archivo):
# from utils.pcoords_extraction import extract_and_store_pcoord_sets
# out_json = extract_and_store_pcoord_sets(pdb_path)
# app.logger.info(f"P coords guardadas en {out_json}")
