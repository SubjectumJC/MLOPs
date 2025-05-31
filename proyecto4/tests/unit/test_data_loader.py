import json
import types

import pandas as pd
import pytest
import sqlalchemy

from services.training_pipeline.data_loader import DataLoader

SAMPLE_JSON = [
    {"id": 1, "feature1": 10, "feature2": "A", "price": 100000},
    {"id": 2, "feature1": 12, "feature2": "B", "price": 120000},
]


def mock_get(*args, **kwargs):  # noqa: D401
    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return SAMPLE_JSON

    return Resp()


def test_download_and_store(monkeypatch, tmp_path):
    # Patch requests.get
    import requests

    monkeypatch.setattr(requests, "get", mock_get)

    # Patch engine to in-memory SQLite
    engine = sqlalchemy.create_engine("sqlite://")
    monkeypatch.setattr(DataLoader, "pg_engine", engine)

    dl = DataLoader()
    df = dl.download_and_store()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

    # Verify table written
    tables = engine.inspect(engine).get_table_names()
    assert DataLoader.RAW_TABLE in tables
