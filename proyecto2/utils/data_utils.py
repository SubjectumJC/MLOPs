import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina nulos y hace ajustes simples de tipos si fuera necesario.
    """
    df = df.dropna()
    return df

def train_and_log_model(df: pd.DataFrame) -> None:
    """
    Entrena un RandomForest y registra métricas y modelo en MLflow.
    Adicionalmente, hace el registro en el Model Registry con nombre "CoverTypeModel".
    """
    if 'Cover_Type' not in df.columns:
        print("No se encontró 'Cover_Type'. Entrenamiento abortado.")
        return

    X = df.drop(columns=['Cover_Type'])
    y = df['Cover_Type']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    experiment_name = "cover_type_experiment"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name="RandomForest_run"):
        n_estimators = 100
        max_depth = 10

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Métricas
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        mlflow.log_metric("accuracy", acc)
        print(f"Accuracy: {acc}")

        # Loguea el modelo en este run
        mlflow.sklearn.log_model(model, artifact_path="model")

        # Registrar el modelo en el Model Registry con nombre "CoverTypeModel"
        model_uri = mlflow.get_artifact_uri("model")
        mlflow.register_model(model_uri, "CoverTypeModel")

        mlflow.end_run()