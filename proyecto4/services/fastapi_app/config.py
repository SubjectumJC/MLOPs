"""
Configuración para el microservicio FastAPI.
Reutiliza las mismas variables que `.env.example`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


@dataclass(slots=True, frozen=True)
class Settings:
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow_experiment: str = os.getenv("MLFLOW_EXPERIMENT", "mlops_project_final")
    model_stage: str = os.getenv("MODEL_STAGE", "Production")
    server_port: int = int(os.getenv("API_PORT", 8000))
    reload_interval: int = int(os.getenv("MODEL_RELOAD_MINUTES", 15))  # refresco periódico opcional


settings = Settings()