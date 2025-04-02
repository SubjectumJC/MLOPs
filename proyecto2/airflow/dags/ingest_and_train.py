"""
DAG para:
 - Ingestar datos desde la API externa (10 lotes).
 - Entrenar un modelo de clasificación (RandomForest).
 - Registrar métricas y modelo en MLflow.
 - Usar covertype.csv como respaldo si la API falla.
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Importamos rutas y utilidades
from utils.paths import RAW_DATA_DIR, PROCESSED_DATA_DIR
from utils.data_utils import preprocess_data, train_and_log_model

# Variables de entorno definidas en .env
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "http://10.43.101.108:80")
GROUP_ID = os.getenv("GROUP_ID", "1")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'ingest_and_train',
    default_args=default_args,
    description='DAG con fallback a covertype.csv si la API falla',
    schedule_interval=None,
    catchup=False
)

def ingest_data():
    """
    Conecta a la API externa y descarga 10 lotes (batch).
    Si cualquier lote falla al obtenerse, se usa covertype.csv (respaldo) para ese lote.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Ruta a nuestro respaldo local
    fallback_path = RAW_DATA_DIR / "covertype.csv"

    for batch_number in range(1, 11):
        url = f"{EXTERNAL_API_URL}/get_data?group_id={GROUP_ID}&batch={batch_number}"
        csv_path = RAW_DATA_DIR / f"batch_{batch_number}.csv"

        try:
            print(f"Intentando descarga de batch {batch_number} desde: {url}")
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data_json = resp.json()
                df = pd.DataFrame(data_json)
                df.to_csv(csv_path, index=False)
                print(f"Batch {batch_number} descargado con {len(df)} filas -> {csv_path}")
            else:
                print(f"Error {resp.status_code} al obtener batch {batch_number}: {resp.text}")
                # Fallback: usaremos covertype.csv
                if fallback_path.exists():
                    print(f"Usando respaldo local: {fallback_path}")
                    # Guardamos el batch fallback con un nombre
                    df_fallback = pd.read_csv(fallback_path)
                    df_fallback.to_csv(csv_path, index=False)
                else:
                    print("No existe el archivo de respaldo. No se puede continuar.")
                    # Podrías terminar la función o lanzar una excepción
                    return
        except Exception as e:
            print(f"Excepción al descargar batch {batch_number}: {e}")
            # Fallback
            if fallback_path.exists():
                print(f"Usando respaldo local por excepción: {fallback_path}")
                df_fallback = pd.read_csv(fallback_path)
                df_fallback.to_csv(csv_path, index=False)
            else:
                print("No existe el archivo de respaldo. No se puede continuar.")
                return

def train_model():
    """
    Lee todos los CSV de data/raw, los concatena, preprocesa y entrena un modelo en MLflow.
    """
    csv_files = list(RAW_DATA_DIR.glob("batch_*.csv"))
    if not csv_files:
        print("No se encontraron archivos para entrenar. Abortando.")
        return

    # Concatenar todos los lotes
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
    combined_data = pd.concat(dfs, ignore_index=True)
    print(f"Total de registros combinados: {len(combined_data)}")

    # Preprocesar
    processed_df = preprocess_data(combined_data)

    # Guardar en data/processed
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    processed_path = PROCESSED_DATA_DIR / "training_data.csv"
    processed_df.to_csv(processed_path, index=False)

    # Entrenar y registrar en MLflow
    train_and_log_model(processed_df)

ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

ingest_task >> train_task