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

### 3. Configurar la conexión MySQL en Airflow

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

Esta configuración permite que el DAG `penguins_to_mysql` se conecte correctamente a la base de datos MySQL usando los credenciales definidos en el docker-compose.yml.

