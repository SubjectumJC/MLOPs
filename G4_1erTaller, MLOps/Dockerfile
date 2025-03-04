# Usa una imagen base de Python
FROM python:3.10

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY api.py penguin_classifier_gradientboosting.pkl penguin_classifier_randomforest.pkl requirements.txt ./

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto donde correrá el API
EXPOSE 8989

# Comando para ejecutar el API cuando el contenedor se inicie
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8989"]
