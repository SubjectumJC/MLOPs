# Proyecto 4 · MLOps (Grupo 4)

![arquitectura](docs/architecture.svg)

Sistema completo de MLOps para el *dataset de bienes raíces* entregado en el curso.  Orquesta la **recolección, procesamiento, entrenamiento, registro y despliegue** de modelos mediante contenedores, CI/CD y observabilidad.

---

## Tabla de contenidos

1. [Stack de servicios](#stack)
2. [Requisitos](#requisitos)
3. [Instalación rápida](#instalacion)
4. [Variables de entorno](#env)
5. [Flujo de datos](#flujo)
6. [Uso diario](#uso)
7. [CI / CD](#cicd)
8. [Preguntas frecuentes](#faq)

---

<a id="stack"></a>

## 1 · Stack de servicios

| Servicio              | Imagen / Dockerfile          | Puerto host | Descripción                                      |
| --------------------- | ---------------------------- | ----------- | ------------------------------------------------ |
| **Airflow**           | `apache/airflow:2.9.1`       | 8080        | Orquestador de *DAGs* de ingestión/entrenamiento |
| **MLflow**            | `mlflow:2.22.0` *custom*     | 5000        | Tracking & Model Registry                        |
| **MinIO**             | `quay.io/minio/minio:latest` | 9000/9001   | S3 compatible – artefactos de MLflow             |
| **PostgreSQL (meta)** | `postgres:16-alpine`         | 5432        | Metadatos de MLflow                              |
| **PostgreSQL raw**    | `postgres:16-alpine`         | 5433        | Datos crudos                                     |
| **PostgreSQL clean**  | `postgres:16-alpine`         | 5434        | Datos limpios                                    |
| **FastAPI**           | `proyecto4-api`              | 8000        | Infiere con el último modelo *Production*        |
| **Streamlit**         | `proyecto4-ui`               | 8501        | UI para usuarios finales                         |
| **Prometheus**        | `prom/prometheus`            | 9090        | Métricas                                         |
| **Grafana**           | `grafana/grafana`            | 3000        | Dashboards                                       |

---

<a id="requisitos"></a>

## 2 · Requisitos

* Docker ≥ 24 y Docker Compose v2.
* Windows 10/11, macOS o cualquier Linux.
* Conexión a Internet para descargar imágenes.

---

<a id="instalacion"></a>

## 3 · Instalación rápida

```powershell
# clonar el repo
> git clone https://github.com/<tu‑usuario>/proyecto4-mlops.git
> cd proyecto4-mlops

# copiar variables de entorno (o editar)
> copy .env.example .env  # Windows
o
$ cp .env.example .env    # Linux/macOS

# levantar todo
> docker compose pull      # descarga imágenes oficiales
> docker compose build     # compila api / training / ui
> docker compose up -d     # arranca los contenedores
```

*Airflow, MLflow y la API tardan \~1 minuto la primera vez.*

---

<a id="env"></a>

## 4 · Variables de entorno (`.env`)

| Clave                                          | Valor por defecto         | Explicación                          |
| ---------------------------------------------- | ------------------------- | ------------------------------------ |
| `GROUP_NUMBER`                                 | **4**                     | Tu número de grupo en la API externa |
| `DATA_API_URL`                                 | `http://10.43.101.108:80` | Endpoint que devuelve un lote nuevo  |
| `MLFLOW_S3_BUCKET`                             | `mlflow-artifacts`        | Bucket de artefactos                 |
| `AWS_ACCESS_KEY_ID`<br>`AWS_SECRET_ACCESS_KEY` | `minioadmin`              | Credenciales de MinIO                |
| `POSTGRES_*`                                   |  …                        | Usuarios/DBs de las tres instancias  |

> **Tip:** cualquier cambio exige reiniciar el servicio afectado: `docker compose restart mlflow`.

---

<a id="flujo"></a>

## 5 · Flujo de datos & modelos

```mermaid
flowchart LR
  subgraph Airflow
    A[Ingest DAG]\n(API → RAW DB) --> B[Process DAG]\n(RAW → CLEAN)
    B --> C[Train+Register]\n(CLEAN → MLflow + S3)
  end
  C -->|etiqueta Production| ML[MLflow]
  ML --> API(FastAPI) --> UI(Streamlit)
  API --> RAW_DB
```

1. **Ingest DAG** consume la API externa y guarda JSON en `postgres-raw`.
2. **Process DAG** limpia, codifica, y normaliza hacia `postgres-clean`.
3. **Train DAG** entrena, loguea métricas y sube el modelo a MLflow.
4. Al marcar un modelo como *Production*, FastAPI lo sirve sin redeploy.
5. Cada llamada a `/predict` se loguea como dato nuevo (retro‑alimentación).

---

<a id="uso"></a>

## 6 · Uso diario

| Acción                 | Cómo hacerlo                                                   |
| ---------------------- | -------------------------------------------------------------- |
| **Ver Airflow**        | [http://localhost:8080](http://localhost:8080) (admin / admin) |
| **Disparar ingestión** | Trigger del DAG **`ingest_dataset`**                           |
| **Ver experimentos**   | [http://localhost:5000](http://localhost:5000)                 |
| **Actualizar modelo**  | En MLflow → “Promote to Production”                            |
| **Probar API**         | [http://localhost:8000/docs](http://localhost:8000/docs)       |
| **UI final**           | [http://localhost:8501](http://localhost:8501)                 |
| **Grafana**            | [http://localhost:3000](http://localhost:3000) (admin / admin) |

Automatiza el ciclo programando el DAG `ingest_dataset` cada hora:

```python
schedule_interval="0 * * * *"  # cron
```

---

<a id="cicd"></a>

## 7 · CI / CD (GitHub Actions + DockerHub + Argo CD)

* **`.github/workflows/push.yml`**: Compila las imágenes (`api`, `training`, `ui`) y las publica en DockerHub.
* **`.github/workflows/test.yml`**: Ejecuta `pytest` y `ruff`.
* **Argo CD** (k8s/ folder): manifiestos Helm que sincronizan deploys en un cluster.

Para probar el workflow localmente:

```bash
act push -j build-and-publish
```

---

<a id="faq"></a>

## 8 · FAQ / Troubleshooting

| Problema                                | Solución                                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------------------------- |
| **`/.env: not found` en build**         | Asegúrate de tener `.env` en la raíz o elimina la línea `COPY .env .` de Dockerfiles.     |
| **MLflow no arranca**                   | Puerto 5000 ocupado → edita `docker-compose.yml` y cambia `5001:5000`.                    |
| **Airflow muestra "permission denied"** | Borra volumenes `airflow-*` y reinicia: `docker compose down -v && docker compose up -d`. |
| **La API externa devuelve error 429**   | Demasiadas peticiones; espera 1‑2 min y re‑ejecuta.                                       |

---

© 2025 · Pontificia Universidad Javeriana – MLOps · Grupo 4
