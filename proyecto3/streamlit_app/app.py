import os, requests, streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Diabetes Readmission", page_icon="🩺")

@st.cache_resource(show_spinner=False)
def fetch_model_info():
    return requests.get(f"{API_URL}/model").json()

model_info = fetch_model_info()
feature_names = model_info["feature_names"]

st.title("🩺 Predicción de Re‑admisión por Diabetes")

inputs = {}
st.subheader("Ingresa valores para cada característica:")
for feat in feature_names:
    inputs[feat] = st.number_input(feat, value=0.0)

if st.button("Predecir"):
    attr_list = [inputs[f] for f in feature_names]
    with st.spinner("Obteniendo predicción..."):
        r = requests.post(f"{API_URL}/predict", json={"attributes": attr_list})
        st.json(r.json())
    st.caption(f"Modelo: {model_info['name']} v{model_info['version']}")

