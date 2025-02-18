from pathlib import Path
import os

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Asegurar compatibilidad en Docker (cuando el script se ejecuta desde notebooks)
if not BASE_DIR.exists():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas de datos
DATA_DIR = BASE_DIR / "data"
PENGUINS_LTER_PATH = DATA_DIR / "penguins_lter.csv"
PENGUINS_SIZE_PATH = DATA_DIR / "penguins_size.csv"

# Rutas de modelos
MODELS_DIR = BASE_DIR / "models"
GRADIENT_BOOSTING_MODEL = MODELS_DIR / "penguin_classifier_gradientboosting.pkl"
RANDOM_FOREST_MODEL = MODELS_DIR / "penguin_classifier_randomforest.pkl"

# Rutas de notebooks
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Rutas de scripts
SRC_DIR = BASE_DIR / "src"
API_DIR = SRC_DIR / "api"
TRAINING_DIR = SRC_DIR / "training"

# Rutas de Docker
DOCKER_DIR = BASE_DIR / "docker"
DOCKERFILE_PATH = DOCKER_DIR / "Dockerfile"
DOCKER_COMPOSE_PATH = DOCKER_DIR / "docker-compose.yml"

# Rutas de configuración
CONFIG_DIR = BASE_DIR / "config"
REQUIREMENTS_PATH = CONFIG_DIR / "requirements.txt"

# Crear directorios si no existen
def ensure_dirs():
    for directory in [
        DATA_DIR, MODELS_DIR, NOTEBOOKS_DIR, SRC_DIR, API_DIR, TRAINING_DIR, DOCKER_DIR, CONFIG_DIR
    ]:
        directory.mkdir(parents=True, exist_ok=True)

ensure_dirs()

# Imprimir rutas para depuración
print(f"🔹 BASE_DIR: {BASE_DIR}")
print(f"🔹 MODELS_DIR: {MODELS_DIR}")
print(f"🔹 DATA_DIR: {DATA_DIR}")
print(f"🔹 NOTEBOOKS_DIR: {NOTEBOOKS_DIR}")
