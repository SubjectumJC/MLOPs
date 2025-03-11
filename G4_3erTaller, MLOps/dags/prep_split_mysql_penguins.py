from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from datetime import datetime, timedelta
import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

def process_penguins(**kwargs):
    # Conexión a MySQL (asegúrate de que el connection id 'MySQL_id' esté configurado)
    mysql_hook = MySqlHook(mysql_conn_id='MySQL_id')
    engine = mysql_hook.get_sqlalchemy_engine()

    # Leer datos de la tabla 'penguins'
    df = pd.read_sql("SELECT * FROM penguins", engine)
    print("Datos originales:", df.head())

    # Filtrar filas con valor 'NULL' en species (si corresponde)
    print("Conteo de species:", df['species'].value_counts(dropna=False))
    df = df[df['species'] != 'NULL']

    # Separamos la variable objetivo
    y = df['species']
    # Eliminamos la columna objetivo para preprocesamiento
    df.drop(columns='species', inplace=True)

    # Identificar columnas numéricas y categóricas
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Crear pipeline para procesamiento numérico
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    # Crear pipeline para procesamiento categórico
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )

    # Dividir en train (80%) y test (20%)
    df_train, df_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)
    print("Tamaño train:", df_train.shape, "Tamaño test:", df_test.shape)

    # Ajustar el preprocesador con los datos de entrenamiento
    preprocessor.fit(df_train)

    # Transformar ambos conjuntos
    train_transformed_array = preprocessor.transform(df_train)
    test_transformed_array = preprocessor.transform(df_test)

    # Obtener nombres de características:
    # Las columnas numéricas se mantienen y las categóricas se obtienen del one-hot encoder
    num_features = list(numeric_cols)
    cat_features = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_cols)
    feature_names = num_features + list(cat_features)

    train_transformed = pd.DataFrame(train_transformed_array, columns=feature_names)
    test_transformed = pd.DataFrame(test_transformed_array, columns=feature_names)

    # Agregar la variable objetivo con el nombre 'species'
    train_transformed['species'] = y_train.reset_index(drop=True)
    test_transformed['species'] = y_test.reset_index(drop=True)

    print("Datos transformados (train):", train_transformed.head())
    print("Datos transformados (test):", test_transformed.head())

    # Guardar el pipeline preprocesador
    model_dir = "/opt/airflow/models"
    os.makedirs(model_dir, exist_ok=True)
    pipeline_path = os.path.join(model_dir, "preprocessor_pipeline.pkl")
    with open(pipeline_path, "wb") as f:
        pickle.dump(preprocessor, f)
    print("Pipeline guardado en:", pipeline_path)

    # Eliminar tablas si existen
    mysql_hook.run("DROP TABLE IF EXISTS penguins_train;")
    mysql_hook.run("DROP TABLE IF EXISTS penguins_test;")

    # Escribir los datos transformados en MySQL
    train_transformed.to_sql('penguins_train', con=engine, if_exists='replace', index=False)
    test_transformed.to_sql('penguins_test', con=engine, if_exists='replace', index=False)
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
