
# Proyecto MLOps - Clasificación de Tipo de Cobertura Forestal

Este proyecto implementa un entorno de MLOps completo usando Docker Compose, diseñado para ejecutarse tanto localmente como en una máquina virtual Linux. El objetivo es construir un pipeline de extremo a extremo para entrenar y servir un modelo de clasificación de cobertura forestal.

## Estructura del Proyecto

```
proyecto2/
├── airflow/
│   └── dags/
│       └── ingest_and_train.py
├── interface/
│   ├── Dockerfile
│   └── app.py
├── inference_api/
│   ├── Dockerfile
│   └── main.py
├── minio/
│   └── data/
├── mysql/
│   └── data/
├── data/
│   ├── raw/
│   │   └── covertype.csv (respaldo local)
│   └── processed/
├── utils/
│   ├── paths.py
│   └── data_utils.py
├── .env
├── docker-compose.yml
└── README.md
```

## Tecnologías utilizadas

- **Airflow**: Orquestación de pipelines.
- **MLflow**: Registro de experimentos y modelos.
- **MinIO**: Almacenamiento de artefactos.
- **MySQL**: Base de datos para MLflow.
- **FastAPI**: API de inferencia.
- **Streamlit**: Interfaz gráfica de usuario.
- **Docker Compose**: Orquestación de servicios.

## 🚀 Instrucciones para ejecutar

### 1. Prerrequisitos

- Docker
- Docker Compose

### 2. Clonar el repositorio y preparar entorno

```bash
git clone <url-del-repo>
cd proyecto2
```

### 3. Verifica o crea el archivo `.env`

Debe contener las variables de entorno necesarias (ver ejemplo en este repositorio).

### 4. Construir y levantar el entorno

```bash
docker-compose down -v
docker-compose up --build
```

### 5. Accede a las interfaces

| Servicio     | URL                            |
|--------------|--------------------------------|
| Airflow      | http://localhost:8080          |
| MLflow       | http://localhost:5000          |
| MinIO        | http://localhost:9000          |
| FastAPI Docs | http://localhost:8000/docs     |
| Interfaz     | http://localhost:8503          |

## 🧠 Flujo general

1. Airflow ejecuta un DAG que:
    - Descarga datos desde una API externa (o usa `covertype.csv` como respaldo).
    - Preprocesa los datos.
    - Entrena un modelo (RandomForest) y lo registra en MLflow.
2. La API de inferencia usa el modelo registrado para responder predicciones.
3. La interfaz gráfica permite probar el modelo fácilmente.

## Requisitos del Taller

Este proyecto cumple todos los puntos requeridos por el taller:

- ✔️ Orquestación con Airflow
- ✔️ Registro en MLflow con artefactos en MinIO y metadata en MySQL
- ✔️ Entrenamiento desde API externa (con respaldo local)
- ✔️ Inferencia vía FastAPI
- ✔️ Interfaz gráfica con Streamlit
- ✔️ Despliegue en VM con Docker Compose

## Prueba en máquina virtual

1. Instala Docker y Docker Compose en la VM.
2. Copia el proyecto a la VM.
3. Ejecuta `docker-compose up --build` dentro de la VM.
4. Accede a los servicios usando la IP pública o privada de la VM.

---

Desarrollado como solución integral para el Proyecto 2 de MLOps (2025).

Alejandro Jiménez Calderón
Luis Cruz
Marc Saint