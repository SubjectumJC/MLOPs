
# Proyecto Final MLOps 2025 – Grupo 4

![ci](https://github.com/<usuario>/proyecto4/actions/workflows/ci.yml/badge.svg)
![license](https://img.shields.io/github/license/<usuario>/proyecto4)

> **Última actualización**: 2025-05-31

Este repositorio contiene la **implementación end‑to‑end** del sistema descrito en el documento “MLOPS_Proyecto_Final_2025.pdf”.  
Incluye recolección de datos, entrenamiento de un autoencoder tabular con explicabilidad **SHAP**, API de inferencia y dashboard, todo orquestado con **Docker Compose** para desarrollo local y **Helm + Argo CD** para producción en Kubernetes.

---

## Tabla de contenidos
1. [Arquitectura](#arquitectura)
2. [Requisitos](#requisitos)
3. [Primeros pasos](#primeros-pasos)
4. [Comandos make (opcional)](#comandos-make-opcional)
5. [Estructura del repositorio](#estructura-del-repositorio)
6. [Variables de entorno](#variables-de-entorno)
7. [Pruebas](#pruebas)
8. [Despliegue en Kubernetes](#despliegue-en-kubernetes)
9. [CI/CD](#cicd)

---

## Arquitectura

```
┌─────────────────────┐
│   Docker Compose    │   ← desarrollo local
└────────┬────────────┘
         │
         ▼
┌──────────────┐   SHAP + métricas   ┌──────────────┐
│  training    │ ───────────────►   │   MLflow UI   │
└──────────────┘                    └──────────────┘
    │                                    ▲
    │ modelo Production                  │ artefactos (MinIO)
    ▼                                    │
┌──────────────┐        predicciones  ┌──────────────┐
│    FastAPI   │ ───────────────────► │ Streamlit UI │
└──────────────┘                     └──────────────┘
```

*En producción, los servicios se despliegan en K8s mediante Helm; Argo CD sincroniza el chart.*

---

## Requisitos

| Herramienta | Versión mínima | Nota |
|-------------|----------------|------|
| **Docker** | 24 | Incluye Compose v2 |
| **GNU Make** | opcional | Solo si quieres usar make; en Windows instala con Chocolatey `choco install make` |
| **Python 3.11** | para ejecutar las pruebas | *(no necesario para usar Docker Compose)* |

---

## Primeros pasos

```powershell
git clone https://github.com/<usuario>/proyecto4.git
cd proyecto4

# 1) .env definitivo ya incluido; duplica si quieres un override local
copy .env .env.local  # opcional

# 2) Levanta la pila
docker compose up -d --build

# 3) Entrena el primer modelo
docker compose run --rm training

# 4) Abre:
start http://localhost:5000      # MLflow
start http://localhost:8501      # Streamlit
start http://localhost:8000/docs # FastAPI docs
```

Para detener todo:

```powershell
docker compose down -v
```

---

## Comandos make (opcional)

| Comando | Acción |
|---------|--------|
| `make docker-up` | Levanta y compila la pila |
| `make docker-down` | Detiene y limpia |
| `make test` | Suite pytest |
| `make lint` | Ruff |
| `make typecheck` | Mypy |

*(Requiere GNU Make).*

---

## Estructura del repositorio

```
├── docker-compose.yml
├── .env
├── Makefile
├── services/
│   ├── training_pipeline/
│   ├── fastapi_app/
│   └── streamlit_ui/
├── docker/
│   ├── Dockerfile.training
│   ├── Dockerfile.api
│   └── Dockerfile.ui
├── charts/mlops/
├── infra/argo/
├── airflow/dags/
└── tests/
```

---

## Variables de entorno

Las principales ya vienen definidas en `.env`; ejemplos:

| Variable | Valor |
|----------|-------|
| `MLFLOW_TRACKING_URI` | http://mlflow:5000 |
| `MLFLOW_S3_ENDPOINT_URL` | http://minio:9000 |
| `DATA_API_URL` | http://10.43.101.108:80 |

---

## Pruebas

```powershell
poetry install --with dev
make test
```

---

## Despliegue en Kubernetes

```bash
helm upgrade --install mlops charts/mlops -n mlops --create-namespace
kubectl apply -f infra/argo/mlops-app.yaml   # Argo CD (opcional)
```

---

## CI/CD

El workflow `.github/workflows/ci.yml`:

1. Ejecuta pruebas.
2. Construye y publica imágenes `training`, `api`, `ui`.
3. Argo CD actualiza el cluster.

Asegura los secrets en GitHub:

```
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

---

