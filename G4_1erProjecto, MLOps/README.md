# MLOps - Proyecto 1 (2025)

## Descripción

Este proyecto tiene como objetivo construir un pipeline de Machine Learning utilizando TensorFlow Extended (TFX) y herramientas de MLOps. Se implementa un flujo de procesamiento de datos que incluye la ingesta, validación, transformación y evaluación de datos para entrenar modelos de aprendizaje automático.

## Autores

Grupo 4, MLOPs 
- Alejandro
- Luis
- Mark

## Requisitos previos

Para ejecutar el proyecto, se requiere:
- Docker y Docker Compose
- Python 3.9 o superior (solo si se ejecuta sin Docker)
- Git (opcional)

## Instalación y configuración

1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd MLOps_Proyecto1_2025
   ```

2. Construir y ejecutar el contenedor Docker:
   ```bash
   docker-compose up --build
   ```

3. Abrir Jupyter Notebook:
   - Copiar la URL mostrada en la terminal, similar a:
     ```
     http://127.0.0.1:8888/?token=<TOKEN>
     ```
   - Pegarla en el navegador para acceder a Jupyter.

4. Abrir el archivo `notebooks/proyecto1.ipynb` y ejecutar las celdas en orden.

## Estructura del proyecto

```
MLOps_Proyecto1_2025/
├── config/
│   └── paths.py  # Definición de rutas del proyecto
├── data/
│   └── covertype.csv.gz  # Dataset comprimido (descargado si no existe)
├── docker/
│   └── Dockerfile  # Configuración de imagen Docker
├── logs/  # Artefactos y metadatos generados
├── notebooks/
│   └── proyecto1.ipynb  # Notebook principal
├── src/
│   └── Dowloadbd.py  # Descarga del dataset
├── docker-compose.yml  # Orquestación del contenedor
├── requirements.txt  # Dependencias del proyecto
└── README.md  # Archivo actual
```

## Funcionalidades principales

1. **Ingesta de datos**: Cargar y validar el dataset `covertype.csv.gz`.
2. **Exploración y selección de características** con Scikit-Learn.
3. **Construcción del pipeline TFX**:
   - `CsvExampleGen`: Convertir datos en TFRecords.
   - `StatisticsGen`: Generar estadísticas descriptivas.
   - `SchemaGen`: Inferir y definir esquemas de datos.
   - `ExampleValidator`: Detectar anomalías.
   - `Transform`: Aplicar transformaciones opcionales.
4. **Seguimiento con ML Metadata**: Gestionar artefactos y registros del pipeline.

## Uso del proyecto

1. **Ejecutar el pipeline**
   - Una vez abierto `proyecto1.ipynb`, ejecutar todas las celdas en orden.
   - Verificar que los artefactos generados se almacenan en `logs/`.

2. **Revisar resultados**
   - Consultar las estadísticas con TensorFlow Data Validation (TFDV).
   - Validar el esquema inferido y hacer ajustes manuales.
   - Examinar los registros almacenados en ML Metadata (`logs/metadata.db`).

## Dependencias

Las dependencias necesarias se encuentran en `requirements.txt`:

```
jupyter
ipywidgets
tfx
tensorflow
pandas
numpy
matplotlib
scikit-learn
requests
tensorflow-data-validation
tensorflow-transform
apache-beam[gcp]
pyarrow
ipykernel
```

Si se ejecuta sin Docker, instalar manualmente:
```bash
pip install -r requirements.txt
```

## Solución de problemas

### Error: `docker-compose` no encontrado
Verificar que Docker y Docker Compose estén instalados correctamente.
```bash
docker --version
docker-compose --version
```

### Jupyter Notebook no carga
Si el contenedor está corriendo pero Jupyter no responde:
```bash
docker ps  # Verificar contenedores activos
docker logs mlops_proyecto1  # Revisar logs
```

Para detener y reiniciar el contenedor:
```bash
docker-compose down
docker-compose up --build
```

## Licencia

Este proyecto es de uso académico y no tiene una licencia específica.
```