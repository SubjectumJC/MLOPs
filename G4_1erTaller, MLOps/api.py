from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

# Cargar ambos modelos en un diccionario
models = {
    "gradient_boosting": joblib.load("penguin_classifier_gradientboosting.pkl"),
    "random_forest": joblib.load("penguin_classifier_randomforest.pkl"),
}

# Crear la aplicación FastAPI
app = FastAPI()

# Definir la estructura del JSON de entrada
class ModelInput(BaseModel):
    model_name: str  # Especifica el modelo a usar ("gradient_boosting" o "random_forest")
    data: Dict[str, Any]  # Datos de entrada para la predicción

# Definir el endpoint de inferencia
@app.post("/predict/")
def predict(input_data: ModelInput):
    try:
        # Verificar que el modelo especificado existe
        if input_data.model_name not in models:
            return {"error": "Modelo no válido. Usa 'gradient_boosting' o 'random_forest'."}

        # Seleccionar el modelo
        model = models[input_data.model_name]

        # Convertir el diccionario de entrada en un DataFrame
        df = pd.DataFrame([input_data.data])

        # Hacer la predicción
        prediction = model.predict(df)

        return {"model_used": input_data.model_name, "prediction": prediction.tolist()}

    except Exception as e:
        return {"error": str(e)}
