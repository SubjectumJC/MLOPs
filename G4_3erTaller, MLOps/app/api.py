from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.pipeline import Pipeline

# Cargar el preprocesador y el modelo en un solo pipeline
pipeline = joblib.load("models/preprocessor_pipeline.pkl")

pipeline = Pipeline([('preprocessor', pipeline),
                     ('random_forest', joblib.load("models/rf_penguins.pkl"))
])
#pipeline.steps.append(["random_forest", joblib.load("models/rf_penguins.pkl")])

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
        if input_data.model_name not in pipeline.named_steps:
            return {"error": "Modelo no válido. Usa 'gradient_boosting' o 'random_forest'."}

        # Seleccionar el modelo
        model = pipeline.named_steps[input_data.model_name]

        # Convertir el diccionario de entrada en un DataFrame
        df = pd.DataFrame([input_data.data])

        # Hacer la predicción
        prediction = pipeline.predict(df)

        # Add date and model columns before saving
        df['prediction_date'] = pd.Timestamp.now()
        df['model_used'] = input_data.model_name
        df.to_csv('log_prediction.csv', mode='a', header=False)

        return {"model_used": input_data.model_name, "prediction": prediction.tolist()}

    except Exception as e:
        return {"error": str(e)}
