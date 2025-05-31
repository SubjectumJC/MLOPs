"""Punto de entrada FastAPI."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import predict
from .state import get_model_objects

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="Proyecto4 MLOps – Inference API", version="1.0.0")


# CORS por defecto para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)


@app.on_event("startup")  # noqa: D401
async def load_model_on_startup():
    """Carga el modelo Production al iniciar la app."""
    get_model_objects()