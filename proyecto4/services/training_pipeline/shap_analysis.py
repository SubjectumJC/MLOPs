"""
Genera gráficos de interpretabilidad con SHAP y los guarda como artefactos
en la ejecución de MLflow.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import mlflow
import numpy as np
import shap
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler

_log = logging.getLogger(__name__)


def log_shap_summary(
    model,
    X_sample: np.ndarray,
    feature_names: List[str],
    artifact_dir: Path,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    explainer = shap.Explainer(model)
    shap_values = explainer(X_sample)
    fig = shap.plots.beeswarm(shap_values, show=False, feature_names=feature_names)
    out_path = artifact_dir / "shap_summary.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    mlflow.log_artifact(str(out_path), artifact_path="explainer")
    _log.info("SHAP summary guardado en MLflow → %s", out_path)