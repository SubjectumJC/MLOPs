import os
import requests
import streamlit as st

# URL de la API de inferencia
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.title("Interfaz de Predicción - Cover Type")
st.write("Completa los campos y presiona el botón para predecir el tipo de cobertura forestal.")

Elevation = st.number_input("Elevation", value=2500.0)
Aspect = st.number_input("Aspect", value=45.0)
Slope = st.number_input("Slope", value=10.0)
Horizontal_Distance_To_Hydrology = st.number_input("Horizontal Distance To Hydrology", value=100.0)
Vertical_Distance_To_Hydrology = st.number_input("Vertical Distance To Hydrology", value=5.0)
Horizontal_Distance_To_Roadways = st.number_input("Horizontal Distance To Roadways", value=300.0)

if st.button("Predecir"):
    payload = {
        "Elevation": Elevation,
        "Aspect": Aspect,
        "Slope": Slope,
        "Horizontal_Distance_To_Hydrology": Horizontal_Distance_To_Hydrology,
        "Vertical_Distance_To_Hydrology": Vertical_Distance_To_Hydrology,
        "Horizontal_Distance_To_Roadways": Horizontal_Distance_To_Roadways,
    }
    try:
        response = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=15)
        if response.status_code == 200:
            resp_json = response.json()
            if "cover_type_prediction" in resp_json:
                st.success(f"Predicción: {resp_json['cover_type_prediction']}")
            else:
                st.error(f"Respuesta inesperada: {resp_json}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error al hacer la solicitud: {e}")