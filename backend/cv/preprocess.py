"""Shared image preprocessing for training and inference (Component 2)."""
from __future__ import annotations

import numpy as np
import torch
from PIL import Image

from cv.model import IMG_SIZE


def to_tensor(img: Image.Image) -> torch.Tensor:
    """PIL image -> normalized CHW float tensor at IMG_SIZE."""
    img = img.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.asarray(img).astype(np.float32) / 255.0      # HWC
    arr = (arr - 0.5) / 0.5                                 # [-1, 1]
    return torch.from_numpy(arr).permute(2, 0, 1)          # CHW
