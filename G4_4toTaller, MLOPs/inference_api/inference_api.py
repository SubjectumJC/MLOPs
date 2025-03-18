import os
import mlflow
import mlflow.sklearn
from flask import Flask, request, jsonify

app = Flask(__name__)

# Leer IP/puerto del MLflow server de las variables de entorno
mlflow_host = os.getenv("MLFLOW_HOST", "localhost")
mlflow_port = os.getenv("MLFLOW_PORT", "5000")

tracking_uri = f"http://{mlflow_host}:{mlflow_port}"
mlflow.set_tracking_uri(tracking_uri)

# Nombre y versión de modelo en MLflow Model Registry
model_name = "mi_modelo_random_forest"
model_version = 1

# Cargar el modelo
model_uri = f"models:/{model_name}/{model_version}"
loaded_model = mlflow.sklearn.load_model(model_uri)

@app.route("/predict", methods=["POST"])
def predict():
    """
    Espera un JSON con la clave "features", que sea una lista de listas:
    {
      "features": [[5.1, 3.5, 1.4, 0.2], [6.2, 3.1, 5.1, 1.8]]
    }
    """
    data = request.get_json()
    features = data.get("features", [])
    prediction = loaded_model.predict(features).tolist()
    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    # API se expone en el puerto 5001, mapeado al host
    app.run(host="0.0.0.0", port=5001)