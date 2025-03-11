import os
import pickle
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

def train_and_save_model(**kwargs):
    # Conexión a MySQL usando el connection id configurado en Airflow
    mysql_hook = MySqlHook(mysql_conn_id='MySQL_id')
    engine = mysql_hook.get_sqlalchemy_engine()

    # Leer la base de datos de entrenamiento
    df_train = pd.read_sql("SELECT * FROM penguins_train WHERE species IS NOT NULL", engine)
    print("Datos de entrenamiento:", df_train.head())

    print(df_train.describe())

    #df_train = df_train.dropna(subset=['species'], axis = 0)
    #print(df_train.info())
    # Suponiendo que 'species' es la variable objetivo (target)
    target = "species"
    X = df_train.drop(columns=[target])
    y = df_train[target]
    
    # Entrenar un modelo Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    
    # Directorio donde guardar el modelo (asegúrate de que este directorio esté montado o persistente)
    model_dir = "/opt/airflow/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "rf_penguins.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(rf, f)
    print("Modelo guardado en:", model_path)

    # Leer la base de datos de test
    df_test = pd.read_sql("SELECT * FROM penguins_test WHERE species IS NOT NULL", engine)
    print("Datos de test:", df_test.head())

    # Suponiendo que 'species' es la variable objetivo (target)
    target = "species"
    X_test = df_test.drop(columns=[target])
    y_test = df_test[target]

    # Calcular el F1-score macro en el set de test
    y_pred = rf.predict(X_test)
    f1 = f1_score(y_test, y_pred, average='macro')
    print("F1-score macro en el set de test:", f1)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'train_random_forest_penguins',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    train_model = PythonOperator(
        task_id='train_and_save_model',
        python_callable=train_and_save_model,
        provide_context=True
    )

    train_model
