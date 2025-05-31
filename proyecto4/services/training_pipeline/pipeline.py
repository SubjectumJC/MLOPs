"""
`pipeline.py` – Orquestación end‑to‑end del entrenamiento.

Pasos:
1. Descargar lote -> RAW
2. Limpieza y pre‑procesamiento -> CLEAN
3. Split train/val
4. Entrenar modelo Lightning (TabularRegressor)
5. Registrar modelo y métricas en MLflow
6. Generar SHAP y subir artefacto
7. Comparar con modelo en *Production* y promover si mejora RMSE
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import mlflow
import numpy as np
import pandas as pd
import sklearn.compose as sc
import sklearn.model_selection as sms
import sklearn.pipeline as sp
import sklearn.preprocessing as skp
from lightning import Trainer
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint

from .config import settings
from .data_loader import DataLoader
from .model import TabularRegressor
from .shap_analysis import log_shap_summary

_log = logging.getLogger(__name__)
EXPERIMENT_NAME = settings.mlflow_experiment


# ---------------------------------------------------------------- utilities
def _build_preprocess(df: pd.DataFrame) -> Tuple[sp.Pipeline, np.ndarray, np.ndarray, list[str]]:
    y = df.pop("price").values
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    num_pipe = sp.Pipeline(
        steps=[("imputer", skp.SimpleImputer(strategy="median")), ("scaler", skp.StandardScaler())]
    )
    cat_pipe = sp.Pipeline(
        steps=[("imputer", skp.SimpleImputer(strategy="most_frequent")), ("encoder", skp.OneHotEncoder(handle_unknown="ignore"))]
    )

    preprocessor = sc.ColumnTransformer(
        transformers=[
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols),
        ]
    )

    X = preprocessor.fit_transform(df)
    feature_names = (
        num_cols
        + preprocessor.named_transformers_["cat"].named_steps["encoder"].get_feature_names_out(cat_cols).tolist()
    )
    return preprocessor, X, y, feature_names


# ---------------------------------------------------------------- pipeline
def run_training() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    loader = DataLoader()

    # 1️⃣ RAW
    raw_df = loader.download_and_store()

    # 2️⃣ CLEAN
    clean_df = raw_df.dropna(subset=["price"]).reset_index(drop=True)
    _log.info("DataFrame limpio -> %d filas", len(clean_df))

    preprocessor, X, y, feature_names = _build_preprocess(clean_df)

    # 3️⃣ Split
    X_train, X_val, y_train, y_val = sms.train_test_split(X, y, test_size=0.2, random_state=42)

    # 4️⃣ Entrenamiento
    with mlflow.start_run(run_name=f"train_{datetime.utcnow().isoformat(timespec='seconds')}") as run:
        mlflow.sklearn.log_model(preprocessor, "preprocessor")

        model, train_loader, val_loader = TabularRegressor.from_numpy(X_train, y_train, X_val, y_val)

        ckpt_cb = ModelCheckpoint(monitor="val_rmse", mode="min", save_top_k=1)
        trainer = Trainer(
            max_epochs=50,
            callbacks=[ckpt_cb, EarlyStopping(monitor="val_rmse", mode="min", patience=5)],
            deterministic=True,
        )
        trainer.fit(model, train_loader, val_loader)

        # 5️⃣ Métricas
        best_ckpt = ckpt_cb.best_model_path
        mlflow.pytorch.log_model(model, "model")
        mlflow.log_param("best_checkpoint", best_ckpt)
        mlflow.log_metrics(trainer.callback_metrics)

        # 6️⃣ SHAP
        sample_idx = np.random.choice(X_val.shape[0], size=min(500, X_val.shape[0]), replace=False)
        artifact_dir = Path(settings.artifacts_root) / run.info.run_id
        log_shap_summary(model, X_val[sample_idx], feature_names, artifact_dir)

        # 7️⃣ Promoción automática
        client = mlflow.tracking.MlflowClient()

        current_rmse = trainer.callback_metrics["val_rmse"].item()
        _log.info("RMSE actual: %.4f", current_rmse)

        prod_versions = client.get_latest_versions(EXPERIMENT_NAME, stages=[settings.model_stage])
        best_rmse = float("inf")
        if prod_versions:
            prod_run = client.get_run(prod_versions[0].run_id)
            best_rmse = float(prod_run.data.metrics.get("val_rmse", "inf"))
            _log.info("RMSE producción actual: %.4f", best_rmse)

        if current_rmse < best_rmse:
            mv = mlflow.register_model(f"runs:/{run.info.run_id}/model", EXPERIMENT_NAME)
            new_version = mv.version

            client.set_model_version_tag(EXPERIMENT_NAME, new_version, "val_rmse", str(current_rmse))
            client.transition_model_version_stage(
                name=EXPERIMENT_NAME,
                version=new_version,
                stage=settings.model_stage,
                archive_existing_versions=True,
            )
            _log.info("🎉 Promovido nuevo modelo versión %s -> %s", new_version, settings.model_stage)
        else:
            _log.info("Modelo no supera producción (%.4f ≥ %.4f)", current_rmse, best_rmse)
