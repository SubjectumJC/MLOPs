from pathlib import Path

# Ruta raíz del proyecto (toma la ubicación de este archivo y sube dos niveles)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Carpetas de datos
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Carpeta de modelos (MLflow puede escribir aquí si no usa MinIO directamente)
MODELS_DIR = ROOT_DIR / "mlflow" / "models"

# Carpeta de experimentos (si MLflow no usa MinIO)
MLRUNS_DIR = ROOT_DIR / "mlflow" / "mlruns"

# DAGs de Airflow
DAGS_DIR = ROOT_DIR / "airflow" / "dags"

# API de inferencia
INFERENCE_API_DIR = ROOT_DIR / "inference_api"

# Interfaz gráfica
INTERFACE_DIR = ROOT_DIR / "interface"

# Verificación opcional: crear directorios si no existen (solo en desarrollo local)
def ensure_directories_exist():
    for path in [RAW_DATA_DIR,
                 PROCESSED_DATA_DIR,
                 MODELS_DIR, MLRUNS_DIR]:
        path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_directories_exist()
