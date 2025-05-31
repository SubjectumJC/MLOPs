"""
Carga y valida la configuración del microservicio a partir de variables de entorno
o, opcionalmente, de un archivo .env.

Los nombres y valores por defecto están calcados de `.env.example`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)  # Permite override local sin tocar el contenedor


@dataclass(slots=True, frozen=True)
class Settings:
    # --- conexión API de datos ------------------------------------------------
    data_api_url: str = os.getenv("DATA_API_URL", "http://10.43.101.108:80")   # :contentReference[oaicite:1]{index=1}
    group_number: int = int(os.getenv("GROUP_NUMBER", 4))

    # --- bases de datos -------------------------------------------------------
    pg_raw_dsn: str = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','mlops')}:"
        f"{os.getenv('POSTGRES_PASSWORD','mlops')}@"
        f"{os.getenv('POSTGRES_HOST_RAW','postgres-raw')}:"
        f"{os.getenv('POSTGRES_PORT_RAW','5432')}/"
        f"{os.getenv('POSTGRES_DB_RAW','raw_data')}"
    )
    pg_clean_dsn: str = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','mlops')}:"
        f"{os.getenv('POSTGRES_PASSWORD','mlops')}@"
        f"{os.getenv('POSTGRES_HOST_CLEAN','postgres-clean')}:"
        f"{os.getenv('POSTGRES_PORT_CLEAN','5432')}/"
        f"{os.getenv('POSTGRES_DB_CLEAN','clean_data')}"
    )

    # --- MLflow ---------------------------------------------------------------
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow_experiment: str = os.getenv("MLFLOW_EXPERIMENT", "mlops_project_final")
    model_stage: str = os.getenv("MODEL_STAGE", "Production")

    # --- artefactos -----------------------------------------------------------
    artifacts_root: Path = Path(os.getenv("ARTIFACTS_ROOT", "/tmp/artifacts")).resolve()


settings = Settings()