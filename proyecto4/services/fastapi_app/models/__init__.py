"""Esquemas Pydantic para requests/responses."""
from __future__ import annotations

from typing import Any, List
from pydantic import BaseModel, Extra


class Features(BaseModel, extra=Extra.allow):  # acepta cualquier columna adicional
    """Representa un registro tabular con campos dinámicos."""


class PredictionResponse(BaseModel):
    predictions: List[float]