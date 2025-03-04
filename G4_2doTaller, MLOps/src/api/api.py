# src/api/api.py

import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import joblib

# Añadir la raíz del proyecto a sys.path si no está ya incluida
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Importa la ruta a la carpeta de modelos desde config.paths
from config.paths import MODELS_DIR

app = FastAPI()

def load_models():
    """
    Carga archivos .pkl de la carpeta 'models/'.
    """
    models_dict = {}
    if not MODELS_DIR.exists():
        return models_dict

    for file in MODELS_DIR.iterdir():
        if file.suffix == ".pkl":
            model_name = file.stem
            try:
                models_dict[model_name] = joblib.load(file)
                print(f"[INFO] Modelo {model_name} cargado.")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar {file.name}: {e}")
    return models_dict

models_cache = load_models()

class ModelInput(BaseModel):
    model_name: str
    data: Dict[str, Any]

@app.post("/predict/")
def predict(input_data: ModelInput):
    global models_cache
    # Recargamos por si hay nuevos modelos
    models_cache = load_models()

    if input_data.model_name not in models_cache:
        return {"error": f"El modelo '{input_data.model_name}' no existe en {MODELS_DIR}."}

    model = models_cache[input_data.model_name]
    df = pd.DataFrame([input_data.data])

    try:
        pred = model.predict(df)
        return {
            "model_used": input_data.model_name,
            "prediction": pred.tolist()
        }
    except Exception as e:
        return {"error": str(e)}