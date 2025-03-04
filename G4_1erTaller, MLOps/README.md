
# Taller 1 - MLOps: Clasificación de Pingüinos 🐧

Este proyecto forma parte del **Taller 1 de MLOps**, donde se desarrolla una API con **FastAPI** para realizar inferencia sobre la especie de pingüinos utilizando modelos preentrenados. Adicionalmente, el proyecto incluye la creación de una imagen Docker para la API.

---

## 📋 Objetivos del Taller
1. Procesar los datos y crear modelos predictivos.
2. Desarrollar una API que permita la inferencia del modelo entrenado usando **FastAPI**.
3. Crear una imagen Docker que exponga la API en el puerto `8989`.

**Bono:**  
El bono de este taller consiste en entregar una funcionalidad adicional en la API que permita seleccionar dinámicamente cuál modelo preentrenado usar para las predicciones.

---

## 📁 Estructura del Proyecto

- `api.py`: Código fuente de la API implementada con FastAPI.
- `Dockerfile`: Archivo para crear la imagen Docker de la API.
- `penguin_classifier_gradientboosting.pkl`: Modelo preentrenado con Gradient Boosting.
- `penguin_classifier_randomforest.pkl`: Modelo preentrenado con Random Forest.
- `requirements.txt`: Lista de dependencias necesarias para el proyecto.

---

## 🚀 Cómo ejecutar el proyecto

### Requisitos previos
- Python 3.9 o superior
- Docker (opcional si deseas ejecutar la API en un contenedor)

### Instalación local

1. Clona este repositorio:
   ```bash
   git clone https://github.com/SubjectumJC/MLOPs.git
   cd MLOPs
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la API localmente usando Uvicorn:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8989 --reload
   ```

4. Accede a la documentación interactiva de la API:
   ```
   http://localhost:8989/docs
   ```

---

## 🐋 Ejecutar con Docker

1. Construye la imagen Docker:
   ```bash
   docker build -t penguin_app .
   ```

2. Ejecuta el contenedor:
   ```bash
   docker run -p 8989:8989 penguin_app
   ```

3. Accede a la documentación de la API en:
   ```
   http://localhost:8989/docs
   ```

---

## 🧪 Uso de la API

### Endpoint `/predict/`
Este endpoint permite hacer una predicción especificando cuál modelo usar (`gradient_boosting` o `random_forest`).

#### Ejemplo de solicitud:
```bash
curl -X 'POST'   'http://localhost:8989/predict/'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
    "model_name": "random_forest",
    "data": {
      "culmen_length_mm": 45.0,
      "culmen_depth_mm": 18.5,
      "flipper_length_mm": 210.0,
      "body_mass_g": 4500.0,
      "island_Biscoe": 1,
      "island_Dream": 0,
      "island_Torgersen": 0,
      "sex_Male": 1,
      "sex_Female": 0
    }
  }'
```

#### Respuesta esperada:
```json
{
  "model_used": "random_forest",
  "prediction": ["Adelie"]
}
```

---

## 📦 Dependencias

Las principales dependencias del proyecto están en `requirements.txt` e incluyen:

- FastAPI
- Uvicorn
- Joblib
- NumPy
- Pydantic
- Scikit-learn
- Pandas

---
