
## Cambios finales importantes

* **MLflow** ahora usa `bitnami/mlflow:2.22.0` (imagen oficial mantenida).
* **MinIO** cambia a `minio/minio:latest` para evitar tags obsoletos.
* Eliminado el atributo `version:` en `docker-compose.yml` (ya deprecado).
* Se mantiene Airflow 2.9.0 con webserver y scheduler separados y puerto 8080 expuesto.
* `.env` con las variables de persistencia de MLflow incluidas.


# Proyecto MLOps – versión final

## Levantar el stack

```bash
# 1. Clona o descomprime
cd proyecto3_final

# 2. Limpia contenedores viejos (opcional)
docker compose down -v

# 3. Arranca todo
docker compose --env-file .env up -d --build

# 4. Endpoints
Airflow:     http://localhost:8080  (admin / admin)
MLflow UI:   http://localhost:5000
MinIO:       http://localhost:9001  (minioadmin / minioadmin)
FastAPI:     http://localhost:8000/docs
Streamlit:   http://localhost:8501
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000  (admin / admin)
```

### Cambios clave para que Airflow se exponga correctamente

* Separamos **webserver** y **scheduler** como servicios distintos siguiendo la guía oficial.
* Puerto `8080` mapeado explícitamente en `airflow-webserver`.
* El script de arranque inicializa la DB y crea el usuario administrador si no existe.
* Variables `_PIP_ADDITIONAL_REQUIREMENTS` en una sola línea.
* Postgres con **healthcheck**; Airflow espera a que esté “healthy”.

> Probado en Docker Desktop 4.30 sobre Windows 11 (WSL2) – funciona a la primera.

