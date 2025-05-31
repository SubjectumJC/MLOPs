"""
Descarga el batch más reciente de datos desde la API externa y los persiste
en la base RAW_DATA.  Cada llamada a la API simula un *nuevo punto en el tiempo*,
según lo descrito en el PDF del proyecto :contentReference[oaicite:3]{index=3}.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import pandas as pd
import requests
from sqlalchemy import create_engine

from .config import settings

_log = logging.getLogger(__name__)


class DataLoader:
    """Encapsula el acceso a la API y la persistencia en Postgres."""

    RAW_TABLE = "raw_housing_data"

    def __init__(self) -> None:
        self.api_url = settings.data_api_url
        self.pg_engine = create_engine(settings.pg_raw_dsn, future=True)

    # --------------------------------------------------------------------- API
    def fetch_batch(self) -> pd.DataFrame:
        """
        Llama a `GET /housing` (supuesto endpoint) con el número de grupo.
        La API devuelve un JSON con la estructura descrita en el PDF.
        """
        url = f"{self.api_url}/housing?group={settings.group_number}"
        _log.info("Solicitando datos a %s", url)
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        rows: List[Dict[str, Any]] = resp.json()
        df = pd.DataFrame(rows)
        _log.info("Recibidos %d registros", len(df))
        return df

    # ------------------------------------------------------------- persistencia
    def save_raw(self, df: pd.DataFrame) -> None:
        """Guarda el DataFrame en la tabla RAW (append)."""
        _log.info("Guardando batch en %s", self.RAW_TABLE)
        df.to_sql(self.RAW_TABLE, self.pg_engine, if_exists="append", index=False)

    # ------------------------------------------------------ API + persistencia
    def download_and_store(self) -> pd.DataFrame:
        df = self.fetch_batch()
        self.save_raw(df)
        return df