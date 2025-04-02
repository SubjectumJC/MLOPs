FROM apache/airflow:2.6.2

# AIRFLOW USUARIO POR DEFECTO
USER airflow

# Copiamos requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Instalamos (sin root) los paquetes
RUN pip install --no-cache-dir -r /tmp/requirements.txt