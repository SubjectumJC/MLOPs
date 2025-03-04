# Taller 2 - MLOps con UV, FastAPI y JupyterLab

En este repositorio encuentras:

1. `Dockerfile` para construir una imagen de **FastAPI** usando **UV**.
2. `docker-compose.yml` que levanta:
   - Un contenedor con **JupyterLab** para entrenar y guardar modelos `.pkl`.
   - Un contenedor con **FastAPI** que carga estos modelos dinámicamente desde `./models`.
3. `api.py` con el endpoint `/predict/`, permitiendo elegir qué modelo usar.
4. `requirements.txt` con las dependencias (incluyendo `uv`).

## Pasos para Ejecutar

1. **Clona este repositorio** o copia estos archivos.
2. **Crea** las carpetas:  
   ```bash
   mkdir models
   mkdir notebooks

La estrcutura del proyecto es la sgt:

G4_2DTALLER_MLOPS/
├── config/
│   ├── __init__.py
│   ├── paths.py
│   └── requirements.txt
├── data/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── models/
├── notebooks/
└── src/
    ├── api/
    │   ├── __init__.py
    │   └── api.py
    └── training/
        ├── __init__.py
        └── train_penguin_v1.py
└── README

Para ejecutar: 
docker-compose build --no-cache
docker-compose up -d