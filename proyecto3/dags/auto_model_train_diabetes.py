# archivo: dags/auto_model_diabetes.py
from __future__ import annotations

import io
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from airflow.decorators import dag, task
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import mlflow
from mlflow.tracking import MlflowClient

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
def auto_model_diabetes():
    """Entrena 3 modelos con 3 features, los registra y
    asciende a Production al que obtenga mayor métrica."""

    # ─────────────────────────────── download
    @task()
    def download_data() -> str:
        local_path = Path("/tmp/diabetes.csv")
        if not local_path.exists():
            r = requests.get(DATA_URL, timeout=60)
            r.raise_for_status()
            pd.read_csv(io.BytesIO(r.content)).to_csv(local_path, index=False)
        return str(local_path)

    # ─────────────────────────────── train + MLflow
    @task()
    def train_and_log(csv_path: str) -> None:
        df = pd.read_csv(csv_path)

        feature_cols = df.columns[2:5]          # solo 3 columnas tras los IDs
        X_raw = df[feature_cols]
        y = df.iloc[:, -1]

        cat_cols = X_raw.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        num_cols = [c for c in feature_cols if c not in cat_cols]

        if cat_cols:
            preproc = ColumnTransformer(
                [
                    ("cat", OneHotEncoder(drop="first", handle_unknown="ignore", sparse=False), cat_cols),
                    ("num", "passthrough", num_cols),
                ]
            )
        else:
            preproc = "passthrough"

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

        mlflow.set_experiment("diabetes_models_3features")
        avg = "binary" if y.nunique() == 2 else "macro"

        client = MlflowClient()
        best_name, best_version, best_score = None, None, -1.0

        for name, estimator in base_models.items():
            pipe = Pipeline([("preprocess", preproc), ("model", estimator)])

            with mlflow.start_run(run_name=name):
                pipe.fit(X_train, y_train)
                preds = pipe.predict(X_test)

                metrics = {
                    "accuracy": accuracy_score(y_test, preds),
                    "f1": f1_score(y_test, preds, average=avg),
                }
                mlflow.log_metrics(metrics)
                mlflow.log_params(estimator.get_params())
                mlflow.sklearn.log_model(pipe, artifact_path="model")

                mv = mlflow.register_model(
                    f"runs:/{mlflow.active_run().info.run_id}/model",
                    f"diabetes_{name}",
                )

                score = metrics["f1"] if avg == "binary" else metrics["accuracy"]
                if score > best_score:
                    best_name, best_version, best_score = mv.name, mv.version, score

        # ── espera a que el mejor modelo esté listo y súbelo a Production
        _wait_until_ready(client, best_name, best_version)
        client.transition_model_version_stage(
            name=best_name,
            version=best_version,
            stage="Production",
            archive_existing_versions=True,
        )

    # util: bloqueante hasta que el modelo pase a READY
    def _wait_until_ready(client: MlflowClient, name: str, version: str, timeout: int = 120):
        start = time.time()
        while time.time() - start < timeout:
            status = client.get_model_version(name, version).status
            if status == "READY":
                return
            time.sleep(5)
        raise TimeoutError(f"Model {name} v{version} not READY after {timeout}s")

    # ─────────────────────────────── dag flow
    train_and_log(download_data())


auto_model_diabetes()
