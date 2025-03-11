# Configuración del Proyecto

## Requisitos Previos
- Docker y Docker Compose instalados
- Git (opcional)

### 1. Clonar el repositorio
Si tienes Git instalado, puedes clonar el repositorio usando:

`git clone ---`

## Pasos de Inicialización

### 2. Crear archivo .env
Primero, crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

`AIRFLOW_UID=1000`

### 3. Acceso a Airflow
Estará disponible en `http://127.0.0.1:8080/`. las credenciales de acceso son tanto usuario y contraseña `airflow`.

### 4. Configurar la conexión MySQL en Airflow

Para configurar la conexión entre Airflow y MySQL, sigue estos pasos en la interfaz web de Airflow:

1. Accede a la interfaz web de Airflow (por defecto en http://localhost:8080)
2. Ve a "Admin" -> "Connections" en el menú superior
3. Haz clic en el botón "+" para agregar una nueva conexión
4. Configura los siguientes campos:
   - Connection Id: `MySQL_id`
   - Connection Type: `MySQL`
   - Host: `mysql` (nombre del servicio en docker-compose)
   - Schema: `my_database`
   - Login: `my_user`
   - Password: `my_password`
   - Port: `3306`

5. Haz clic en "Save" para guardar la conexión

Esta configuración permite que los DAGs se conecten correctamente a la base de datos MySQL usando los credenciales definidos en el docker-compose.yml.

### 5. Ejecución de DAGs

El orden de ejecución es tal como se ve en la siguiente imagen:

![Orden de ejecución](https://github.com/SubjectumJC/MLOPs/blob/feature/data-pipeline/G4_3erTaller%2C%20MLOps/imgs/DAGs.png)

### 6. Test de Inferencia

Es posible hacer la inferencia desde terminal ejecutando el siguiente comando:

`curl -X 'POST' \
  'http://127.0.0.1:8989/predict/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model_name": "random_forest",
  "data": {
    "island": "Torgersen",
    "bill_length_mm": 39.1,
    "bill_depth_mm": 18.7,
    "flipper_length_mm": 181,
    "body_mass_g": 3750,
    "sex": "Male"
}
}'`

o Accediendo via web a `http://127.0.0.1:8989/docs` y probando con el request body:

`{
  "model_name": "random_forest",
  "data": {
    "island": "Torgersen",
    "bill_length_mm": 39.1,
    "bill_depth_mm": 18.7,
    "flipper_length_mm": 181,
    "body_mass_g": 3750,
    "sex": "Male"
}
}`

El resultado esperado es el siguiente:

`{
  "model_used": "random_forest",
  "prediction": [
    "Adelie"
  ]
}`
