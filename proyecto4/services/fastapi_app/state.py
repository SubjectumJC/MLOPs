"""Carga y cachea (singleton) el modelo Production + preprocesador."""
from __future__ import annotations

import logging
from threading import Lock

import mlflow
from mlflow import artifacts, sklearn as ml_sklearn, pytorch as ml_torch
from mlflow.tracking import MlflowClient

from .config import settings

_log = logging.getLogger(__name__)

_PREPROCESSOR = None
_MODEL = None
_LOCK = Lock()


def _load_objects():
    global _PREPROCESSOR, _MODEL  # noqa: PLW0603
    client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
    versions = client.get_latest_versions(settings.mlflow_experiment, stages=[settings.model_stage])
    if not versions:
        _log.error("No hay modelo en stage %s", settings.model_stage)
        return
    model_uri = f"models:/{settings.mlflow_experiment}/{settings.model_stage}"
    _MODEL = ml_torch.load_model(model_uri)
    run_id = versions[0].run_id
    preproc_path = artifacts.download_artifacts(run_id=run_id, artifact_path="preprocessor")
    _PREPROCESSOR = ml_sklearn.load_model(preproc_path)
    _log.info("Modelo y preprocesador cargados desde run %s", run_id)


def get_model_objects():
    if _MODEL is None or _PREPROCESSOR is None:
        with _LOCK:
            if _MODEL is None or _PREPROCESSOR is None:
                _load_objects()
    return _PREPROCESSOR, _MODEL