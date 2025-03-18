# G4_4toTaller_MLOPs

Este proyecto contiene todo lo necesario para:

1. Iniciar una base de datos PostgreSQL para MLflow (en la carpeta `db`).
2. Iniciar un servicio MinIO (en la carpeta `minio`) para almacenar artefactos en modo S3.
3. Levantar MLflow usando un servicio de `systemd` (en la carpeta `mlflow`).
4. Ejecutar JupyterLab dentro de un contenedor Docker (en la carpeta `jupyterlab`), para experimentar y registrar runs en MLflow.
5. Crear y exponer un servicio de inferencia (en la carpeta `inference_api`) que cargue un modelo desde MLflow.
6. **Centralizar** todas las variables relevantes (IPs, puertos, credenciales) en el archivo `paths.env`.

---

## 1. Configurar las variables de entorno en `paths.env`

En la raíz del proyecto hay un archivo llamado **paths.env**. Ábrelo y ajusta los valores según tu entorno.  
Por ejemplo, si todo corre en **la misma máquina**, podrías dejar:

```
DB_HOST=localhost
MINIO_HOST=localhost
MLFLOW_HOST=localhost
```

y así sucesivamente. Deja los puertos como vienen por defecto a menos que tengas conflictos con otros servicios.

> **Importante**: Si tu VM tiene una IP pública o si cada servicio corre en máquinas diferentes, ajusta `DB_HOST`, `MINIO_HOST`, `MLFLOW_HOST` a la IP que corresponda en cada caso.

---

## 2. Crear el entorno virtual MLOps4 (opcional)

En la carpeta raíz del proyecto (G4_4toTaller_MLOPs):

```bash
cd G4_4toTaller_MLOPs
python3 -m venv MLOps4
source MLOps4/bin/activate
```

En Windows, usar:  
`MLOps4\Scripts\activate.bat`  
Este paso es opcional si vas a usar directamente los contenedores Docker y systemd (no es estrictamente necesario).

---

## 3. Base de datos (PostgreSQL)

1. Ve a la carpeta `db`:
   ```bash
   cd db
   ```
2. Levanta el servicio de base de datos con docker-compose. **Nota**: para que Docker Compose cargue las variables de `paths.env`, ejecuta:
   ```bash
   docker compose --env-file ../paths.env -f docker-compose-db.yaml up -d
   ```
   Esto levantará un contenedor **postgres_db** con:
   - Usuario: `${DB_USER}`
   - Contraseña: `${DB_PASS}`
   - Base de datos: `${DB_NAME}`
   - Puerto: `${DB_PORT}` (mapeado a 5432 interno del contenedor)

3. Regresa a la carpeta raíz:
   ```bash
   cd ..
   ```

---

## 4. Servicio de MinIO (almacenamiento de artefactos S3)

1. Ve a la carpeta `minio`:
   ```bash
   cd minio
   ```
2. Inicia MinIO con:
   ```bash
   docker compose --env-file ../paths.env -f docker-compose-minio.yaml up -d
   ```
   - Consola Web: `http://<MINIO_HOST>:<MINIO_CONSOLE_PORT>`  
   - API S3: `http://<MINIO_HOST>:<MINIO_PORT>`  
   - Usuario: `${MINIO_ACCESS_KEY}`  
   - Contraseña: `${MINIO_SECRET_KEY}`  
3. Crea un **bucket** en la consola de MinIO, con nombre `${MINIO_BUCKET}` (por defecto `mlflows3`).  
4. Regresa a la carpeta raíz:
   ```bash
   cd ..
   ```

---

## 5. Configurar y levantar MLflow con systemd

1. Abre `mlflow/mlflow_serv.service` y verifica la ruta de `EnvironmentFile=` sea la real, por ejemplo:
   ```ini
   EnvironmentFile=/home/estudiante/G4_4toTaller_MLOPs/paths.env
   ```
   Ajusta si tu proyecto está en otra ubicación.

2. Copia el archivo de servicio a `/etc/systemd/system/` (o similar):
   ```bash
   sudo cp mlflow/mlflow_serv.service /etc/systemd/system/mlflow_serv.service
   ```

3. Recarga los demonios:
   ```bash
   sudo systemctl daemon-reload
   ```

4. Habilita e inicia el servicio:
   ```bash
   sudo systemctl enable mlflow_serv.service
   sudo systemctl start mlflow_serv.service
   ```
5. Verifica:
   ```bash
   sudo systemctl status mlflow_serv.service
   ```
   Debe aparecer “active (running)”. MLflow escuchará en **puerto** `${MLFLOW_PORT}` (por defecto 5000).

---

## 6. JupyterLab para experimentación

1. Ve a la carpeta `jupyterlab`:
   ```bash
   cd jupyterlab
   ```
2. Construye la imagen Docker:
   ```bash
   docker build -t jupyterlab .
   ```
3. Inicia el contenedor (puedes usar la variable de puerto, pero aquí lo dejamos fijo):
   ```bash
   docker run -it --name jupyterlab --rm \
     -p 8888:8888 \
     -v $PWD:/work \
     jupyterlab:latest
   ```
   - El contenedor mostrará una URL con token para ingresar a JupyterLab (puerto 8888).

4. Abre `experiment.ipynb`.  
   Este Notebook lee las **variables** de entorno desde `paths.env` (si las tienes exportadas) para configurar `mlflow.set_tracking_uri(...)`.

---

## 7. API de Inferencia

1. Ve a la carpeta `inference_api`:
   ```bash
   cd inference_api
   ```
2. Construye la imagen:
   ```bash
   docker build -t inference_api .
   ```
3. Inicia el contenedor:
   ```bash
   docker run -it --name inference_api --rm \
     -p 5001:5001 \
     inference_api:latest
   ```
4. Haz una petición POST a `http://<MLFLOW_HOST>:5001/predict` con un JSON, por ejemplo:
   ```json
   {
     "features": [[5.1, 3.5, 1.4, 0.2]]
   }
   ```
   La respuesta será un JSON con la predicción.

> Ajusta dentro de `inference_api.py` el nombre y versión del modelo. Asegúrate de haber **registrado un modelo** con ese nombre y versión en MLflow.

---

## 🚀 Comandos para levantar cada servicio

---

### 🔵 3. Levantar Base de datos (PostgreSQL)

```bash
cd G4_4toTaller_MLOPs/db
docker compose --env-file ../paths.env -f docker-compose-db.yaml up -d
cd ..
```

---

### 🟠 4. Levantar MinIO (S3 Storage)

```bash
cd G4_4toTaller_MLOPs/minio
docker compose --env-file ../paths.env -f docker-compose-minio.yaml up -d
cd ..
```

---

### 🟢 5. Levantar MLflow Tracking Server (systemd)

```bash
sudo cp mlflow/mlflow_serv.service /etc/systemd/system/mlflow_serv.service
sudo systemctl daemon-reload
sudo systemctl enable mlflow_serv.service
sudo systemctl start mlflow_serv.service
sudo systemctl status mlflow_serv.service
```

---

### 🟣 6. Levantar JupyterLab para experimentación

```bash
cd G4_4toTaller_MLOPs/jupyterlab
docker build -t jupyterlab .
docker run -it --name jupyterlab --rm \
  -p 8888:8888 \
  -v $PWD:/work \
  --env-file ../paths.env \
  jupyterlab:latest
cd ..
```

---

### 🔴 7. Levantar API de Inferencia

```bash
cd G4_4toTaller_MLOPs/inference_api
docker build -t inference_api .
docker run -it --name inference_api --rm \
  -p 5001:5001 \
  --env-file ../paths.env \
  inference_api:latest
cd ..
```

---

## 📂 Estructura del proyecto:

```
G4_4toTaller_MLOPs
├── README.md
├── paths.env
├── db
│   └── docker-compose-db.yaml
├── minio
│   ├── docker-compose-minio.yaml
│   └── data_minio/
├── mlflow
│   ├── mlflow_serv.service
│   └── README_MLFLOW.txt
├── jupyterlab
│   ├── Dockerfile
│   ├── requirements.txt
│   └── experiment.ipynb
└── inference_api
    ├── Dockerfile
    └── inference_api.pyy         # Código Flask para la API

---