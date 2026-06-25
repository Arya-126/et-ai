"""Small CNN for genuine-vs-counterfeit note classification (Component 2).
Deliberately compact so it trains on CPU in a couple of minutes.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from cv.spec import CLASSES, IMG_SIZE  # noqa: F401  (re-exported for compatibility)


class NoteCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # 64
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 32
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 16
            nn.AdaptiveAvgPool2d(4),                                       # 4x4
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))
