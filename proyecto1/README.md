# MLOps Proyecto 1

Este proyecto desarrolla un pipeline de Machine Learning utilizando MLOps. Se incluyen etapas de ingesta, validación, transformación de datos y versionamiento del código.

## Instalación y Uso

1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPO>

2. Construir y ejecutar el contenedor Docker:
   ```bash
   docker build -t mlops-proyecto1 .
   docker run -p 8888:8888 mlops-proyecto1
   ```

3. Acceder a JupyterLab:
   - Abrir el navegador web y visitar: http://localhost:8888
   - No se requiere token de acceso
   - Navegar hasta el notebook `DataExploration.ipynb` para explorar el proceso de análisis de datos
