# config/paths.py
# -*- coding: utf-8 -*-
import os
from pathlib import Path

# Definir la raíz del proyecto (dos niveles arriba de este archivo)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Directorios principales
CONFIG = PROJECT_ROOT / "config"
DATA = PROJECT_ROOT / "data"
DOCS = PROJECT_ROOT / "docs"
DRIVERS = PROJECT_ROOT / "drivers"
LOGS = PROJECT_ROOT / "logs"
NOTEBOOKS = PROJECT_ROOT / "notebooks"
SRC = PROJECT_ROOT / "src"

# Definir la ubicación del archivo comprimido
DATA_FILENAME = "covertype.csv.gz"
DATA_PATH = DATA / DATA_FILENAME

# Definir paths para data limpia (si lo requieres)
CLEAN_DATA_FILENAME = "covertype_clean.csv"
CLEAN_DATA_PATH = DATA / CLEAN_DATA_FILENAME

# Definir la ubicación del pipeline TFX
PIPELINE_ROOT = LOGS / "tfx_pipeline_output"
METADATA_PATH = LOGS / "metadata.db"

# Asegurar que las carpetas existen
for path in [DATA, LOGS, CONFIG, NOTEBOOKS, SRC, DOCS, DRIVERS]:
    path.mkdir(parents=True, exist_ok=True)