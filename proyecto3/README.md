# Proyecto 3 – Diabetes Readmission MLOps Pipeline

Este repositorio contiene una **plataforma MLOps completa** (todo‑en‑uno, basada en Docker Compose) para entrenar, versionar y servir un modelo de *machine learning* que predice la readmisión hospitalaria de pacientes diabéticos.  
Incluye *ingestión de datos* automatizada, *entrenamiento continuo*, *registro de modelos*, *serving online*, UI de usuario final, pruebas de carga y observabilidad.

---

## Arquitectura

| Servicio | Imagen / Dockerfile | Puerto local | Descripción breve |
|----------|--------------------|--------------|-------------------|
| **Airflow** | `airflow_dockerfile` | `8080` | Orquestador de pipelines. Contiene DAGs para ingestión y entrenamiento. |
| **MLflow** | `mlflow_dockerfile` | `5000` | Tracking y registro de modelos. Artifacts almacenados en volumen. |
| **PostgreSQL (airflow)** | `postgres:15-alpine` | `5432` | Base de datos de metadata de Airflow. |
| **PostgreSQL (mlflowdb)** | `postgres:15-alpine` | `5433` (interno `5432`) | Backend store de MLflow. |
| **API FastAPI** | `api_dockerfile` | `8000` | Servicio REST `/predict` que expone el modelo en producción. |
| **Streamlit UI** | `streamlit_dockerfile` | `8501` | Front‑end interactivo para probar el modelo. |
| **Locust** | `locustio/locust` | `8089` | Generador de carga para la API. |
| **Prometheus** | `prom/prometheus` | `9090` | Recolección de métricas. |
| **Grafana** | `grafana/grafana` | `3000` | Dashboards y alertas. |

Todos los contenedores comparten la red de *docker‑compose* y montan volúmenes para persistencia.

---

## Requisitos previos

* Docker ≥ 20.10  
* docker‑compose ≥ v2  
* GNU make (opcional)

---

## Puesta en marcha rápida

```bash
# 1. Clona el repo
git clone https://github.com/<tu‑org>/proyecto3.git
cd proyecto3

# 2. Copia o edita el archivo de variables de entorno
cp .env.example .env        # o edita .env ya incluido
# ── variables más importantes ──
# AIRFLOW_UID=5000           # tu UID para evitar problemas de permisos
# MLFLOW_TRACKING_URI=http://mlflow:5000

# 3. Construye y levanta toda la stack (≈ 10 min la primera vez)
docker compose up --build -d

# 4. Abre los servicios en tu navegador
open http://localhost:8080   # Airflow (admin: airflow / airflow)
open http://localhost:5000   # MLflow
open http://localhost:8000/docs   # API Swagger
open http://localhost:8501   # Streamlit
open http://localhost:8089   # Locust
open http://localhost:3000   # Grafana (admin / admin)
```

Para apagar y limpiar: `docker compose down -v`.

---

## Dataset

Los DAGs descargan automáticamente el *Diabetes Hospital Readmission* dataset (UCI).  
No necesitas descargar nada manualmente; el *task* `download_data` lo hace y guarda la tabla `raw_data` en PostgreSQL.

---

## Airflow DAGs

| DAG | Frecuencia (`schedule`) | Tareas principales |
|-----|-------------------------|--------------------|
| `ingest_diabetes` | `@daily` | Descarga datos, *train/test split*, guarda en DB. |
| `train_models_diabetes_simple` | `@daily` | Entrena RandomForest, registra en MLflow. |
| `auto_model_train_diabetes` | `@weekly` | Búsqueda de hiper‑parámetros + registro. |

DAGs deshabilitados por defecto — actívalos desde la UI o con la CLI.

---

## API REST

* **POST `/predict`**

```jsonc
{
  "records": [
    { "race": "Caucasian", "gender": "Female", "age": "[60-70)" }
  ]
}
```

Respuesta:

```jsonc
{
  "predictions": [0.18]
}
```

* **GET `/health`** – *liveness probe*.

Swagger disponible en `/docs`.

---

## Front‑end (Streamlit)

La UI muestra:

1. Nombre y versión del modelo en producción (vía MLflow API).  
2. Campos para elegir *race*, *gender* y *age*.  
3. Cuando envías el formulario, llama a la API y dibuja la probabilidad de readmisión.

---

## Pruebas de carga (Locust)

```bash
locust --host http://localhost:8000
```

Abre la UI (`localhost:8089`), define nº de usuarios y tasa de *spawn*.

---

## Observabilidad

* **Prometheus** recoge métricas de contenedores y la API.  
* **Grafana** trae un *dashboard* genérico y otro de métricas personalizadas (`api_request_duration_seconds`).

---

## Estructura de carpetas

```
proyecto3/
├─ api/               # Servicio FastAPI
├─ dags/              # Airflow DAGs
├─ ml/                # Scripts de entrenamiento local
├─ mlruns/            # Artefactos de MLflow
├─ infra/             # Configs de Prometheus/Grafana
├─ ui/                # Streamlit app
├─ locust/            # Escenarios de prueba
├─ docker-compose.yml
└─ *.dockerfile
```

---