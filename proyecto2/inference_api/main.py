import os
import mlflow
import mlflow.pyfunc
from fastapi import FastAPI
from pydantic import BaseModel

# MLflow Tracking URI
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(mlflow_tracking_uri)

app = FastAPI(title="Inference API", description="Servicio de inferencia para Cover Type")

# Nombre del modelo en MLflow Model Registry
MODEL_NAME = "CoverTypeModel"
MODEL_STAGE = "Production"

# Cargamos el modelo registrado (se asume que ya está en stage Production)
try:
    model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Modelo '{MODEL_NAME}' en stage '{MODEL_STAGE}' cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar modelo '{MODEL_NAME}' stage '{MODEL_STAGE}': {e}")
    model = None

class InferenceRequest(BaseModel):
    Elevation: float
    Aspect: float
    Slope: float
    Horizontal_Distance_To_Hydrology: float
    Vertical_Distance_To_Hydrology: float
    Horizontal_Distance_To_Roadways: float
    # Agrega más campos si tu modelo los necesita.

@app.get("/")
def root():
    return {"message": "API de inferencia para Cover Type operativa."}

@app.post("/predict")
def predict_cover_type(request: InferenceRequest):
    if model is None:
        return {"error": "No hay modelo disponible en este momento."}

    data_dict = request.dict()
    input_data = [data_dict]
    prediction = model.predict(input_data)
    return {"cover_type_prediction": int(prediction[0])}