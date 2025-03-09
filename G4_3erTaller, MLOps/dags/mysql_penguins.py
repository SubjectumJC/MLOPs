from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns

def download_and_store_penguins(**kwargs):
    # Descargar el dataset de penguins usando seaborn
    df = sns.load_dataset("penguins")
    # Opcional: eliminar filas con valores faltantes
    df = df.dropna()

    # Conexión a MySQL
    mysql_hook = MySqlHook(mysql_conn_id='MySQL_id')
    engine = mysql_hook.get_sqlalchemy_engine()

    # Crear la tabla si no existe (ajusta los tipos de datos según necesites)
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS penguins (
        species VARCHAR(50),
        island VARCHAR(50),
        bill_length_mm FLOAT,
        bill_depth_mm FLOAT,
        flipper_length_mm INT,
        body_mass_g INT,
        sex VARCHAR(10),
        year INT
    );
    """
    mysql_hook.run(create_table_sql)
    
    # Guardar el dataframe en la tabla 'penguins'
    # Si la tabla ya existe, se agregan los registros
    df.to_sql('penguins', con=engine, if_exists='append', index=False)
    print("Datos insertados correctamente en MySQL.")

# Definición del DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'penguins_to_mysql',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    task_download_and_store = PythonOperator(
        task_id='download_and_store_penguins',
        python_callable=download_and_store_penguins,
        provide_context=True
    )

    task_download_and_store
