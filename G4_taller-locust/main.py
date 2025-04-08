from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import mlflow.pyfunc
from mlflow.tracking import MlflowClient

app = FastAPI()

class PenguinInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    island: str
    sex: str

def load_production_model():
    client = MlflowClient()
    for model_name in ["PenguinClassifier-RandomForest", "PenguinClassifier-GradientBoosting"]:
        versions = client.get_latest_versions(model_name, stages=["Production"])
        if versions:
            return mlflow.pyfunc.load_model(f"models:/{model_name}/Production")
    raise Exception("No hay modelo en producción")

model = load_production_model()

@app.post("/predict")
def predict(penguin: PenguinInput):
    try:
        df = pd.DataFrame([penguin.dict()])
        pred = model.predict(df)
        return {"predicted_species": pred[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
