from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime, timedelta

def drop_penguins_table(**kwargs):
    # Conexión definida en Airflow (asegúrate de que el connection id sea correcto)
    mysql_hook = MySqlHook(mysql_conn_id='MySQL_id')
    # Comando SQL para eliminar la tabla si existe
    drop_sql = "DROP TABLE IF EXISTS penguins;"
    mysql_hook.run(drop_sql)
    print("La tabla 'penguins' ha sido eliminada (si existía).")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'drop_penguins_table_dag',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    drop_table = PythonOperator(
        task_id='drop_penguins_table',
        python_callable=drop_penguins_table,
        provide_context=True
    )

    drop_table
