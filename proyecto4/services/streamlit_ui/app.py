"""
Streamlit dashboard – Proyecto Final MLOps 2025 (Grupo 4)

• Lista versiones del experimento 💾
• Muestra métricas (RMSE, MAE, R²)
• Visualiza gráfico SHAP de cada run
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from mlflow import tracking
from mlflow.artifacts import download_artifacts

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT", "mlops_project_final")


@st.cache_data(ttl=300)  # cache 5 min
def load_runs() -> pd.DataFrame:
    client = tracking.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    exp = client.get_experiment_by_name(EXPERIMENT_NAME)
    if exp is None:
        return pd.DataFrame()
    runs = client.search_runs([exp.experiment_id], order_by=["attributes.start_time DESC"])
    rows = []
    for run in runs:
        rows.append(
            {
                "run_id": run.info.run_id,
                "rmse": run.data.metrics.get("val_rmse"),
                "mae": run.data.metrics.get("val_mae"),
                "r2": run.data.metrics.get("val_r2"),
                "start_time": pd.to_datetime(run.info.start_time, unit="ms"),
            }
        )
    return pd.DataFrame(rows)


def load_shap(run_id: str) -> Path | None:
    try:
        return Path(
            download_artifacts(run_id=run_id, artifact_path="explainer/shap_summary.png")
        )
    except Exception:
        return None


st.set_page_config(page_title="MLOps 2025 Dashboard", layout="wide")
st.title("📊 Dashboard – Proyecto Final MLOps 2025")

runs_df = load_runs()
if runs_df.empty:
    st.warning("No se encontraron ejecuciones en el experimento.")
    st.stop()

st.subheader("Histórico de métricas")
st.dataframe(
    runs_df[["run_id", "rmse", "mae", "r2", "start_time"]]
    .sort_values("start_time", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
)

sel_run = st.selectbox(
    "Selecciona un run para inspeccionar SHAP",
    runs_df["run_id"],
    format_func=lambda r: f"{r[:8]} – RMSE {runs_df.loc[runs_df.run_id==r,'rmse'].values[0]:.3f}",
)

shap_path = load_shap(sel_run)
if shap_path and shap_path.exists():
    st.image(str(shap_path), caption=f"SHAP summary – {sel_run[:8]}")
else:
    st.info("El run seleccionado no contiene artefacto SHAP.")
