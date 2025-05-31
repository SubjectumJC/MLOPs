"""
CLI del microservicio basada en Typer:

$ poetry run python -m services.training_pipeline.cli run               # entrenamiento completo
$ poetry run python -m services.training_pipeline.cli fetch            # solo descarga datos
"""
from __future__ import annotations

import logging

import typer

from .data_loader import DataLoader
from .pipeline import run_training

app = typer.Typer(add_completion=False)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@app.command()
def fetch() -> None:  # noqa: D401
    """Descarga el batch más reciente y lo guarda en RAW_DATA."""
    DataLoader().download_and_store()


@app.command()
def run() -> None:  # noqa: D401
    """Ejecuta el pipeline completo de entrenamiento."""
    run_training()


if __name__ == "__main__":
    app()
