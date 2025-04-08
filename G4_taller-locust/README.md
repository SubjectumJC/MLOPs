
# 🐧 Taller MLOps - FastAPI + MLflow + Locust

Este proyecto demuestra un flujo completo de MLOps que incluye entrenamiento de modelos con MLflow, creación de una API con FastAPI, despliegue mediante Docker y `docker-compose`, pruebas de carga con Locust, y uso de MLflow UI para seguimiento de experimentos y registro de modelos.

---

## 🚀 Estructura del proyecto

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── train_penguin.py
├── main.py
├── locustfile.py
├── .env
└── README.md
```

---

## ⚙️ Requisitos

- Docker
- Docker Compose
- Cuenta en DockerHub
- Git (opcional para MLflow)
- MLflow instalado si deseas correr local

---

## 🐳 1. Construcción del contenedor

### Dockerfile

Crea un archivo `Dockerfile` con:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Construcción de la imagen

```bash
docker build -t tu_usuario/fastapi-inferencia:latest .
```

### Subida a DockerHub

```bash
docker login
docker push tu_usuario/fastapi-inferencia:latest
```

> Asegúrate de reemplazar `tu_usuario` por tu nombre de usuario de DockerHub.

---

## 🔬 2. Entrenamiento del modelo y registro en MLflow

El script `train_penguin.py` entrena dos modelos (`RandomForest`, `GradientBoosting`) y los registra en MLflow.

### Entrenamiento desde Docker Compose

```bash
docker-compose run --rm api python train_penguin.py
```

Esto conecta con el contenedor `mlflow` (que también se levanta con Compose) para registrar los modelos.

---

## 🔧 3. Configuración de `docker-compose.yml`

```yaml
services:
  api:
    image: tu_usuario/fastapi-inferencia:latest
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mlflow

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    command: mlflow server --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0

  locust:
    image: locustio/locust
    volumes:
      - .:/mnt/locust
    ports:
      - "8089:8089"
    working_dir: /mnt/locust
    command: -f locustfile.py --host http://api:8000
    depends_on:
      - api
```

---

## 🔎 4. MLflow UI

Accede a la interfaz de MLflow en:

```
http://localhost:5000
```

Aquí puedes visualizar:
- Experimentos
- Modelos registrados
- Versiones de modelo

---

## 📊 5. Pruebas de carga con Locust

1. Lanza Locust:

```bash
docker-compose up locust
```

2. Abre en tu navegador:

```
http://localhost:8089
```

3. Ingresa número de usuarios y tasa (spawn rate), luego presiona "Start swarming".

---

## 🧪 6. Probar la API

Una vez la API esté corriendo:

```bash
docker-compose up api
```

Puedes hacer pruebas manuales con `curl` o Postman a:

```
POST http://localhost:8000/predict
Content-Type: application/json

{
  "island": "Torgersen",
  "sex": "MALE",
  "bill_length_mm": 39.1,
  "bill_depth_mm": 18.7,
  "flipper_length_mm": 181,
  "body_mass_g": 3750
}
```

---

## ✅ Resumen

- Entrenamiento y registro en MLflow ✔️
- Contenerización y despliegue con Docker ✔️
- Despliegue de API con FastAPI ✔️
- MLflow UI para gestión de experimentos ✔️
- Pruebas de carga con Locust ✔️

---

## 📎 Créditos

Taller basado en el dataset [Palmer Penguins](https://github.com/allisonhorst/palmerpenguins).

---
