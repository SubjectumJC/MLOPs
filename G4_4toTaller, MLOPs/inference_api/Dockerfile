FROM python:3.9

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías necesarias
RUN pip install --no-cache-dir \
    flask \
    mlflow \
    boto3 \
    awscli \
    scikit-learn \
    pandas \
    numpy \
    psycopg2-binary

WORKDIR /app

COPY inference_api.py .

EXPOSE 5001

CMD ["python", "inference_api.py"]