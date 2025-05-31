"""Airflow DAG que ejecuta el contenedor de entrenamiento cada día a las 02:00 UTC."""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

TRAIN_IMAGE = os.getenv("TRAIN_IMAGE", "training_pipeline:latest")

with DAG(
    dag_id="train_daily",
    description="Entrena y registra un modelo a diario",
    default_args=default_args,
    schedule_interval="0 2 * * *",  # 02:00 UTC
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=["mlops", "training"],
) as dag:
    train = DockerOperator(
        task_id="train_model",
        image=TRAIN_IMAGE,
        api_version="auto",
        auto_remove=True,
        command="python -m services.training_pipeline.cli run",
        network_mode="bridge",
        environment={
            "MLFLOW_TRACKING_URI": os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"),
            "MLFLOW_EXPERIMENT": os.getenv("MLFLOW_EXPERIMENT", "mlops_project_final"),
        },
    )
