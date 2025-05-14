import os, json, mlflow, pandas as pd
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

DATA_DIR = '/data/clean'
TRAIN_CSV = os.path.join(DATA_DIR, 'train.csv')
VAL_CSV   = os.path.join(DATA_DIR, 'val.csv')

FEATURES = [
    'time_in_hospital','num_lab_procedures','num_procedures',
    'num_medications','number_outpatient','number_emergency',
    'number_inpatient','number_diagnoses'
]

def load_data():
    df_train = pd.read_csv(TRAIN_CSV)
    df_val   = pd.read_csv(VAL_CSV)
    X_train, y_train = df_train[FEATURES], df_train['readmitted']
    X_val, y_val     = df_val[FEATURES], df_val['readmitted']
    return X_train, X_val, y_train, y_val

def main():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    mlflow.set_experiment("diabetes-readmission")

    X_train, X_val, y_train, y_val = load_data()

    with mlflow.start_run():
        model = LogisticRegression(max_iter=300)
        model.fit(X_train, y_train)

        preds = model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        mlflow.log_metric("val_accuracy", acc)

        # save feature schema
        schema_path = "model_info.json"
        with open(schema_path, "w") as f:
            json.dump({"features": FEATURES}, f)
        mlflow.log_artifact(schema_path, artifact_path=".")

        mlflow.sklearn.log_model(model, "model", registered_model_name="diabetes-model")

        # Promote best model
        client = mlflow.tracking.MlflowClient()
        best_run = max(
            client.search_runs("diabetes-readmission"),
            key=lambda r: r.data.metrics.get("val_accuracy", 0)
        )
        mv = client.get_latest_versions("diabetes-model", stages=["None"])[-1]
        client.transition_model_version_stage(
            name="diabetes-model",
            version=mv.version,
            stage="Production",
            archive_existing_versions=True
        )

if __name__ == "__main__":
    main()


