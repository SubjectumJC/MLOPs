import numpy as np
import torch
from lightning import Trainer

from services.training_pipeline.model import TabularRegressor


def test_model_forward():
    X = np.random.rand(10, 5).astype(np.float32)
    y = np.random.rand(10).astype(np.float32)

    model, train_loader, val_loader = TabularRegressor.from_numpy(X, y, X, y, batch_size=2)
    trainer = Trainer(fast_dev_run=True)
    trainer.fit(model, train_loader, val_loader)

    preds = model(torch.tensor(X))
    assert preds.shape[0] == 10
