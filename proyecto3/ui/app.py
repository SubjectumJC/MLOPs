# archivo: app.py  (Streamlit)
# -----------------------------------------------------------
# UI: muestra el modelo (nombre + versión) y envía:
# {"records": [{race, gender, age}]}
# -----------------------------------------------------------
import os
import requests
import streamlit as st

API_URL      = os.getenv("API_URL", "http://localhost:8000")
MODEL_NAME   = os.getenv("MODEL_NAME", "diabetes_random_forest")   # solo a título informativo
MODEL_STAGE  = os.getenv("MODEL_STAGE", "Production")              # idem

st.set_page_config(page_title="Diabetes Readmission 🩺", page_icon="🩺")

# ────────────────────────────
# Pregunta al endpoint /health qué versión hay en uso
# ────────────────────────────
@st.cache_resource(show_spinner=False)
def fetch_model_meta():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        if r.ok:
            return r.json().get("model_version", "unknown")
    except Exception:
        pass
    return "unavailable"

MODEL_VERSION = fetch_model_meta()

# ────────────────────────────
# 3 features que usa el modelo
# ────────────────────────────
RACE_OPTS = [
    "Caucasian", "AfricanAmerican", "Asian", "Hispanic", "Other", "?"
]
GENDER_OPTS = ["Male", "Female", "Unknown/Invalid"]
AGE_OPTS = [
    "[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
    "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)",
]

# ────────────────────────────
# UI
# ────────────────────────────
st.title("🩺 Predicción de Re-admisión (3 variables)")

st.caption(f"**Modelo activo:** `{MODEL_NAME}` · stage `{MODEL_STAGE}` ·version `{MODEL_VERSION}`")

race   = st.selectbox("Raza (race)",    RACE_OPTS)
gender = st.selectbox("Género (gender)", GENDER_OPTS)
age    = st.selectbox("Edad (age)",      AGE_OPTS)

if st.button("Predecir"):
    payload = {"records": [{"race": race, "gender": gender, "age": age}]}

    with st.spinner("Consultando modelo…"):
        res = requests.post(f"{API_URL}/predict", json=payload)

    if res.ok:
        st.success(f"Respuesta del modelo: {res.json()}")
    else:
        st.error(f"Error {res.status_code}: {res.text}")
