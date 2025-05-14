from fastapi import FastAPI, Response
from pydantic import BaseModel
import mlflow, os, json, pandas as pd, time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

MODEL_NAME = "diabetes-model"

app = FastAPI(title="Diabetes Readmission API")

REQUESTS = Counter("inference_requests_total", "Total inference requests")
LATENCY = Histogram("inference_latency_seconds", "Latency per request")

def load_production_model():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    model_uri = f"models:/{MODEL_NAME}/Production"
    model = mlflow.pyfunc.load_model(model_uri)
    client = mlflow.tracking.MlflowClient()
    mv = client.get_latest_versions(MODEL_NAME, stages=["Production"])[0]
    info_local = client.download_artifacts(run_id=mv.run_id, path="model_info.json")
    with open(info_local, "r") as f:
        model_info = json.load(f)
    return model, mv, model_info

model, model_version, model_info = load_production_model()
FEATURES = model_info["features"]

class Patient(BaseModel):
    attributes: list[float]

@app.post("/predict")
def predict(p: Patient):
    start = time.time()
    REQUESTS.inc()
    if len(p.attributes) != len(FEATURES):
        return {"error": f"Se esperaban {len(FEATURES)} atributos"}
    df = pd.DataFrame([p.attributes], columns=FEATURES)
    pred = model.predict(df)[0]
    LATENCY.observe(time.time() - start)
    return {"prediction": int(pred)}

@app.get("/model")
def model_metadata():
    return {
        "name": MODEL_NAME,
        "version": model_version.version,
        "run_id": model_version.run_id,
        "feature_names": FEATURES
    }

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

