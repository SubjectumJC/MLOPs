# src/Downloadbd.py

import requests
import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto está en sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.paths import DATA_PATH 
                                    
def download_covertype_data():
    """
    Descarga covertype.data.gz y lo deja en la carpeta data/ como covertype.csv.gz,
    SIN descomprimir, para que TFX lo use directamente.
    """

    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/covtype/covtype.data.gz"

    # Usamos .csv.gz para que TFX lo reconozca como CSV comprimido
    csv_gz_path = str(DATA_PATH).replace(".data.gz", ".csv.gz")

    if not os.path.exists(csv_gz_path):
        print(f"Descargando archivo comprimido en: {csv_gz_path}")
        r = requests.get(url, stream=True)
        with open(csv_gz_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("¡Descarga completada! Archivo listo para TFX.")
    else:
        print("El archivo comprimido ya existe, no se descarga de nuevo.")

if __name__ == "__main__":
    download_covertype_data()