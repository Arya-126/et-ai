"""Shared image preprocessing for training and inference (Component 2).
torch is imported lazily so the rest of the CV path works without it."""
from __future__ import annotations

import numpy as np
from PIL import Image

from cv.spec import IMG_SIZE


def to_tensor(img: Image.Image):
    """PIL image -> normalized CHW float tensor at IMG_SIZE."""
    import torch  # lazy: only needed when the CNN is in use

    img = img.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.asarray(img).astype(np.float32) / 255.0      # HWC
    arr = (arr - 0.5) / 0.5                                 # [-1, 1]
    return torch.from_numpy(arr).permute(2, 0, 1)          # CHW
