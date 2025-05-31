"""
Modelo de regresión tabular en PyTorch-Lightning que predice el *price* de la
vivienda (objetivo del dataset) :contentReference[oaicite:5]{index=5}.

La arquitectura es un MLP compacto que funciona bien para datos tabulares.
"""
from __future__ import annotations

import math
from typing import Any

import mlflow
import torch
import torch.nn as nn
from lightning import LightningModule
from lightning.pytorch.utilities.types import STEP_OUTPUT
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from torch.utils.data import DataLoader, TensorDataset


class TabularRegressor(LightningModule):
    def __init__(
        self,
        n_features: int,
        learning_rate: float = 1e-3,
        hidden: int = 128,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.ReLU(),
            nn.BatchNorm1d(hidden),
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(),
            nn.Linear(hidden // 2, 1),
        )
        self.criterion = nn.MSELoss()

    # ------------------------------------------------------------------- core
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(1)

    def _common_step(self, batch: Any, stage: str) -> STEP_OUTPUT:
        x, y = batch
        y_hat = self(x)
        loss = self.criterion(y_hat, y)
        self.log(f"{stage}_loss", loss, prog_bar=True, batch_size=len(y))
        return {"y": y.detach().cpu(), "y_hat": y_hat.detach().cpu()}

    def training_step(self, batch: Any, batch_idx: int) -> STEP_OUTPUT:  # noqa: D401, ANN001
        return self._common_step(batch, "train")

    def validation_step(self, batch: Any, batch_idx: int) -> STEP_OUTPUT:  # noqa: D401, ANN001
        return self._common_step(batch, "val")

    def on_validation_epoch_end(self) -> None:
        y_true = torch.cat([o["y"] for o in self.trainer._evaluation_loop.outputs])
        y_pred = torch.cat([o["y_hat"] for o in self.trainer._evaluation_loop.outputs])

        rmse = math.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        self.log_dict({"val_rmse": rmse, "val_mae": mae, "val_r2": r2}, prog_bar=True)

    # -------------------------------------------------------------- optimiser
    def configure_optimizers(self):  # noqa: ANN001, D401
        return torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)

    # ---------------------------------------------------------------- factory
    @staticmethod
    def from_numpy(
        X_train,
        y_train,
        X_val,
        y_val,
        batch_size: int = 256,
        **kwargs,
    ) -> tuple["TabularRegressor", DataLoader, DataLoader]:
        model = TabularRegressor(n_features=X_train.shape[1], **kwargs)
        train_loader = DataLoader(
            TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32)),
            batch_size=batch_size,
            shuffle=True,
        )
        val_loader = DataLoader(
            TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32)),
            batch_size=batch_size,
            shuffle=False,
        )
        return model, train_loader, val_loader