# archivo: dags/train_diabetes_models_simple.py
from __future__ import annotations

import io
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from airflow.decorators import dag, task
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import mlflow
import mlflow.sklearn

DATA_URL = (
    "https://docs.google.com/uc?export=download&confirm="
    "{{VALUE}}&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC"
)

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    start_date=datetime(2025, 5, 1),
    schedule="@once",
    catchup=False,
    default_args=default_args,
    tags=["train", "diabetes", "mlflow"],
)
def train_diabetes_models_simple():
    """Descarga el dataset y entrena tres modelos usando **solo las tres primeras
    variables después de los IDs** (las posiciones 3-5 del CSV original)."""

    # ───────────────────────────────
    # 1. Descarga (o reutiliza) el CSV
    # ───────────────────────────────
    @task()
    def download_data() -> str:
        local_path = Path("/tmp/diabetes.csv")
        if not local_path.exists():
            resp = requests.get(DATA_URL, timeout=60)
            resp.raise_for_status()
            pd.read_csv(io.BytesIO(resp.content)).to_csv(local_path, index=False)
        return str(local_path)

    # ───────────────────────────────
    # 2. Entrenamiento + tracking
    # ───────────────────────────────
    @task()
    def train_and_log(csv_path: str) -> None:
        df = pd.read_csv(csv_path)

        # ▸ columnas 0‑1 → IDs; 2‑4 → tres features requeridas
        feature_cols = df.columns[2:5]          # solo esas tres
        X_raw = df[feature_cols]
        y = df.iloc[:, -1]                      # última columna = target

        # separa categóricas / numéricas según dtype
        cat_cols = X_raw.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        num_cols = [c for c in feature_cols if c not in cat_cols]

        preproc = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(drop="first", 
                                      handle_unknown="ignore",
                                      sparse=False), cat_cols),
                ("num", "passthrough", num_cols),
            ]
        )

        base_models = {
            "log_reg": LogisticRegression(max_iter=1000, n_jobs=1),
            "random_forest": RandomForestClassifier(
                n_estimators=200, max_depth=8, n_jobs=1, random_state=42
            ),
            "grad_boost": GradientBoostingClassifier(random_state=42),
        }

        X_train, X_test, y_train, y_test = train_test_split(
            X_raw, y, test_size=0.2, random_state=42, shuffle=True
        )

        mlflow.set_experiment("diabetes_models_v3")
        avg = "binary" if y.nunique() == 2 else "macro"

        for name, estimator in base_models.items():
            pipe = Pipeline(steps=[("preprocess", preproc), ("model", estimator)])

            with mlflow.start_run(run_name=name):
                pipe.fit(X_train, y_train)

                preds = pipe.predict(X_test)
                mlflow.log_metrics(
                    {
                        "accuracy": accuracy_score(y_test, preds),
                        "f1": f1_score(y_test, preds, average=avg),
                    }
                )
                mlflow.log_params(estimator.get_params())
                mlflow.sklearn.log_model(pipe, artifact_path="model")

                # registro en el Model Registry
                mlflow.register_model(
                    f"runs:/{mlflow.active_run().info.run_id}/model",
                    f"diabetes_{name}",
                )

    # ───────────────────────────────
    # Orquestación
    # ───────────────────────────────
    train_and_log(download_data())

# Instancia el DAG para Airflow
train_diabetes_models_simple()
