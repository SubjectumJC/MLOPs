# archivo: dags/ingest_diabetes_files.py
from datetime import datetime, timedelta
from pathlib import Path
from airflow.decorators import dag, task
import pandas as pd
from sklearn.model_selection import train_test_split
import requests
import io

URL = (
    "https://docs.google.com/uc?export=download&confirm="
    "{{VALUE}}&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC"
)
OUTPUT_DIR = "/opt/airflow/data/diabetes"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    start_date=datetime(2025, 5, 1),
    schedule="@once",
    catchup=False,
    default_args=default_args,
    tags=["ingest", "diabetes"],
)
def ingest_diabetes_files():

    @task()
    def download_csv() -> str:
        """Descarga el CSV y lo devuelve como JSONstring."""
        resp = requests.get(URL, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(io.BytesIO(resp.content))
        return df.to_json(orient="records")

    @task()
    def split_data(raw_json: str) -> dict:
        """Divide en train/test y devuelve ambos como JSONstring."""
        df = pd.read_json(raw_json, orient="records")
        train, test = train_test_split(
            df, test_size=0.2, random_state=42, shuffle=True
        )
        train["subset"] = "train"
        test["subset"] = "test"
        return {
            "train": train.to_json(orient="records"),
            "test": test.to_json(orient="records"),
        }

    @task()
    def save_subsets(json_payload: dict):
        """
        Guarda cada subset en disco:
        - /opt/airflow/data/diabetes/train.parquet
        - /opt/airflow/data/diabetes/test.parquet
        """
        out = Path(OUTPUT_DIR)
        out.mkdir(parents=True, exist_ok=True)

        for subset, json_str in json_payload.items():
            df = pd.read_json(json_str, orient="records")
            # CSV:  df.to_csv(out / f"{subset}.csv", index=False)
            df.to_parquet(out / f"{subset}.parquet", index=False)

    # Flujo del DAG
    raw_json = download_csv()
    splits = split_data(raw_json)
    save_subsets(splits)

ingest_diabetes_files()
