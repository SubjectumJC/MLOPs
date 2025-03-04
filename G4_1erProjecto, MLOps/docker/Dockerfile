# docker/Dockerfile

# Usa una imagen base de Python 3.9
FROM python:3.9

# Evita que Python guarde buffers
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo en el contenedor
WORKDIR /app

# Copiar y luego instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Jupyter
EXPOSE 8888

# Comando por defecto: lanzar un Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--no-browser"]