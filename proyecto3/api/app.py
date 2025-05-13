# app.py -------------------------------------------------------------
import os
import mlflow
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from typing import List

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "diabetes_random_forest")   # registry name
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")

app = FastAPI(title="Diabetes Predictor", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")
class Record(BaseModel):
    # *** Define ONLY the columns expected by the model ***
    age: float
    weight: float
    gender_Male: int  # ← one‑hot columns as produced by pd.get_dummies
    # … add the rest …

class Records(BaseModel):
    records: List[Record]

def _load_model():
    """
    Loads the Production version from the MLflow ModelRegistry.
    Keeps a single global reference (`_model`) so reloads only
    if the stage/version changes.
    """
    global _model, _loaded_version
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = mlflow.tracking.MlflowClient()
    prod = client.get_latest_versions(MODEL_NAME, [MODEL_STAGE])[0]
    if prod.version != _loaded_version:
        _model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
        _loaded_version = prod.version
        logger.info("Loaded %s version %s", MODEL_NAME, _loaded_version)

# initialise
_model, _loaded_version = None, None
_load_model()

@app.get("/health")
def health():
    return {"status": "UP", "model_version": _loaded_version}

@app.post("/predict")
def predict(payload: Records):
    try:
        _load_model()                         # hot‑reload if Registry changed
        df = pd.DataFrame([r.dict() for r in payload.records])
        preds = _model.predict(df)
        return JSONResponse({"predictions": preds.tolist()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
