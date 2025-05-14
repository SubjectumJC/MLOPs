# MLOps Proyecto 3 – **Entrega completa**

Repositorio listo‑para‑usar que cumple cada punto del enunciado:

1. **Airflow** orquesta:
   - Descarga dataset
   - Ingresa a BD *raw*
   - Procesa a BD *clean*
   - Genera particiones *train/val/test* (`15 000` registros por ejecución en *train*)
   - Lanza entrenamiento y registra en **MLflow**

2. **MLflow** con PostgreSQL + MinIO (artefactos) y *auto‑promoción* del mejor modelo a *Production*.

3. **FastAPI** expone inferencia (usa siempre `models:/diabetes-model/Production`) + métricas Prometheus.

4. **Streamlit** consume la API y genera inputs dinámicos según el esquema del modelo.

5. **Prometheus + Grafana** recogen / visualizan métricas de inferencia.

6. **Locust** carga concurrente para dimensionar capacidad.

7. **Kubernetes manifests** en `k8s/` (convertidos con Kompose) para desplegar la misma pila.

---

## Ejecución local rápida

```bash
docker compose up --build          # primera vez
docker compose up -d               # arranque en segundo plano
```

Una vez arriba:

| Servicio      | URL                         | Credenciales |
|---------------|-----------------------------|--------------|
| **Airflow**   | http://localhost:8080       | admin / admin |
| **MLflow**    | http://localhost:5000       | — |
| **FastAPI**   | http://localhost:8000/docs  | — |
| **Streamlit** | http://localhost:8501       | — |
| **Grafana**   | http://localhost:3000       | admin / admin |

`locust -f locust/locustfile.py http://localhost:8000` lanza la prueba de carga.

---

## Estructura

```
.
├── dags/                  # DAGs de Airflow
├── infra/                 # Prometheus/Grafana
├── api/                   # FastAPI
├── streamlit_app/         # UI
├── training/              # Entrenamiento y métrica
├── locust/                # Simulación de usuarios
├── k8s/                   # YAMLs K8s
└── docker-compose.yml
```

