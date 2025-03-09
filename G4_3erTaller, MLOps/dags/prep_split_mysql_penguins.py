from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def process_penguins(**kwargs):
    # Conexión a MySQL (asegúrate de que el connection id 'mysql_penguins' esté configurado en Airflow)
    mysql_hook = MySqlHook(mysql_conn_id='MySQL_id')
    engine = mysql_hook.get_sqlalchemy_engine()

    # Leer datos de la tabla 'penguins'
    df = pd.read_sql("SELECT * FROM penguins", engine)
    print("Datos originales:", df.head())

    # Procesamiento: llenar valores vacíos
    # Separa columnas numéricas y categóricas
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Para las columnas numéricas, imputamos la media
    for col in numeric_cols:
        df[col].fillna(df[col].mean(), inplace=True)
    # Para las columnas categóricas, imputamos la moda
    for col in categorical_cols:
        if not df[col].empty:
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    # Estandarizar las columnas numéricas
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    print("Datos procesados:", df.head())

    # Dividir el dataframe en train (80%) y test (20%)
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    print("Tamaño train:", df_train.shape, "Tamaño test:", df_test.shape)

    # Escribir los datos resultantes en MySQL (reemplaza las tablas si ya existen)
    df_train.to_sql('penguins_train', con=engine, if_exists='replace', index=False)
    df_test.to_sql('penguins_test', con=engine, if_exists='replace', index=False)
    print("Datos guardados en MySQL: 'penguins_train' y 'penguins_test'.")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'process_penguins_mysql',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    process_task = PythonOperator(
        task_id='process_penguins',
        python_callable=process_penguins,
        provide_context=True
    )

    process_task
