FROM python:3.10-slim

WORKDIR /app

# 1. Instalar 'uv' via pip
RUN pip install --no-cache-dir uv

# 2. Copiar todo el proyecto (incluyendo 'config/requirements.txt') al contenedor
COPY . /app

# 3. Instalar dependencias usando uv pip install
RUN uv pip install --system --verbose -r config/requirements.txt

# 4. Exponer puerto 8989
EXPOSE 8989

# 5. Comando que arranca la API con uvicorn
CMD ["uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8989"]