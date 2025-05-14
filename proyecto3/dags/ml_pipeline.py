from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, pandas as pd, requests, sqlalchemy
from sqlalchemy import text
from sklearn.model_selection import train_test_split

RAW_FILE = "/data/raw/diabetes.csv"
CLEAN_FILE = "/data/clean/clean.csv"
TRAIN_FILE = "/data/clean/train.csv"
VAL_FILE   = "/data/clean/val.csv"
TEST_FILE  = "/data/clean/test.csv"
DB_URI = "postgresql+psycopg2://mlflow:mlflow@postgres:5432/mlflow"

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip"

default_args = {"owner":"airflow","retries":1,"retry_delay":timedelta(minutes=5)}

def download_dataset(**_):
    os.makedirs("/data/raw", exist_ok=True)
    if not os.path.isfile(RAW_FILE):
        r = requests.get(URL, stream=True)
        import zipfile, io
        z = zipfile.ZipFile(io.BytesIO(r.content))
        csv_name = [n for n in z.namelist() if n.endswith('.csv')][0]
        with open(RAW_FILE, "wb") as f:
            f.write(z.read(csv_name))

def ingest_raw_to_db(**_):
    engine = sqlalchemy.create_engine(DB_URI)
    df = pd.read_csv(RAW_FILE)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    df.to_sql("diabetes", engine, schema="raw", if_exists="replace", index=False)

def process_clean(**context):
    engine = sqlalchemy.create_engine(DB_URI)
    df = pd.read_csv(RAW_FILE)
    # simple preprocessing
    df = df[['time_in_hospital','num_lab_procedures','num_procedures',
             'num_medications','number_outpatient','number_emergency',
             'number_inpatient','number_diagnoses','readmitted']]
    df = df.dropna()
    os.makedirs("/data/clean", exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS clean"))
    df.to_sql("diabetes", engine, schema="clean", if_exists="replace", index=False)

    # split sets (train batch of 15k each run)
    run_id = context['logical_date'].int_timestamp // (24*3600)  # daily increment
    batch_start = run_id * 15000
    batch_end = batch_start + 15000
    train_df = df.iloc[batch_start:batch_end]
    rest = df.drop(train_df.index)
    val_df, test_df = train_test_split(rest, test_size=0.5, random_state=42)

    train_df.to_csv(TRAIN_FILE, index=False)
    val_df.to_csv(VAL_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

def trigger_training(**_):
    import subprocess, sys
    result = subprocess.run(["python", "/opt/airflow/dags/scripts/run_training.py"], capture_output=True)
    print(result.stdout.decode())
    if result.returncode != 0:
        raise RuntimeError("Training failed")

with DAG(
    dag_id="diabetes_end_to_end",
    default_args=default_args,
    start_date=datetime(2025,1,1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id="download_dataset", python_callable=download_dataset)
    t2 = PythonOperator(task_id="ingest_raw", python_callable=ingest_raw_to_db)
    t3 = PythonOperator(task_id="process_clean", python_callable=process_clean, provide_context=True)
    t4 = PythonOperator(task_id="train_model", python_callable=trigger_training)

    t1 >> t2 >> t3 >> t4

