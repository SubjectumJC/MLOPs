# archivo: dags/ingest_diabetes.py
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.db import provide_session

import pandas as pd
from sklearn.model_selection import train_test_split
import requests
import io
import math

URL = (
    "https://docs.google.com/uc?export=download&confirm="
    "{{VALUE}}&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC"
)
TABLE = "raw_data"
BATCH_SIZE = 15000

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
def ingest_diabetes():
    @task()
    def download_csv() -> pd.DataFrame:
        resp = requests.get(URL, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(io.BytesIO(resp.content))
        return df.to_json(orient="records")

    @task()
    def split_data(raw_json: str):
        df = pd.read_json(raw_json, orient="records")
        train, test = train_test_split(
            df, test_size=0.2, random_state=42, shuffle=True
        )
        train["subset"] = "train"
        test["subset"] = "test"
        return {"train": train.to_json(orient="records"),
                "test": test.to_json(orient="records")}

    @task()
    @provide_session
    def prepare_table(session=None):
        """
        Crea o limpia la tabla raw_data.
        Schema flexible: todas las columnas + `subset` varchar
        """
        pg = PostgresHook(postgres_conn_id="airflow_db")
        col_defs = ", ".join(
            [f"{col} TEXT" for col in ("subset",)]
        )
        # Drop + create for idempotencia
        pg.run(f"DROP TABLE IF EXISTS {TABLE};", autocommit=True)
        pg.run(f"CREATE TABLE {TABLE} (id SERIAL PRIMARY KEY, {col_defs});", autocommit=True)

    @task()
    def insert_batches(json_payload: dict):
        pg = PostgresHook(postgres_conn_id="airflow_db")
        for subset_name, json_str in json_payload.items():
            df = pd.read_json(json_str, orient="records")
            rows = df.to_dict(orient="records")
            n_batches = math.ceil(len(rows) / BATCH_SIZE)
            for i in range(n_batches):
                batch = rows[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
                # usa mogrify para insertar en bloque
                insert_sql, params = pg.insert_rows(table=TABLE, rows=[
                    (row["subset"],)  # amplía con otras columnas
                    for row in batch
                ], target_fields=["subset"], commit_every=0, replace=False)
                pg.run(insert_sql, parameters=params, autocommit=True)

    # DAG flow
    raw_json = download_csv()
    splits = split_data(raw_json)
    prepare_table() >> insert_batches(splits)


ingest_diabetes()
