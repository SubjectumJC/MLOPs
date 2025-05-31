from fastapi.testclient import TestClient
import torch

from services.fastapi_app.main import app
from services.fastapi_app import state


class DummyPreproc:  # noqa: D401
    def transform(self, df):  # noqa: D401
        import numpy as np
        return np.ones((len(df), 5), dtype=float)


class DummyModel(torch.nn.Module):
    def forward(self, x):
        return torch.ones(x.shape[0]) * 123.45


def override_model():
    return DummyPreproc(), DummyModel()


state.get_model_objects = override_model

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_predict():
    payload = [
        {"feature1": 1, "feature2": "A"},
        {"feature1": 2, "feature2": "B"},
    ]
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    preds = resp.json()["predictions"]
    assert all(abs(p - 123.45) < 1e-3 for p in preds)
