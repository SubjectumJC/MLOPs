from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from ..models import Features, PredictionResponse
from ..state import get_model_objects

router = APIRouter()
_log = logging.getLogger(__name__)


@router.get("/health", tags=["health"])  # noqa: D401
def health_check() -> dict[str, str]:
    """Devuelve 200 si el modelo está cargado."""
    preprocessor, model = get_model_objects()
    status = "ready" if model is not None else "loading"
    return {"status": status}


@router.post("/predict", response_model=PredictionResponse, tags=["inference"])  # noqa: D401
def predict(records: List[Features]):  # noqa: D401
    """Realiza inferencia batch. Acepta lista de registros (≥1)."""
    if not records:
        raise HTTPException(status_code=400, detail="Input vacío.")
    preprocessor, model = get_model_objects()
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo aún no disponible.")
    df = pd.DataFrame([r.model_dump() for r in records])
    X = preprocessor.transform(df)
    preds = model(torch.tensor(X, dtype=torch.float32)).detach().cpu().numpy().flatten()
    return PredictionResponse(predictions=np.round(preds, 2).tolist())