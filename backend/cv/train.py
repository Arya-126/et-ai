"""Train the NoteCNN on the synthetic dataset (Component 2). CPU-friendly.
Run:  python -m cv.generate_notes && python -m cv.train
Saves cv/note_cnn.pt.
"""
from __future__ import annotations

import glob
import os
import random

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from cv.model import CLASSES, NoteCNN
from cv.preprocess import to_tensor

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")
WEIGHTS = os.path.join(HERE, "note_cnn.pt")


class NoteDataset(Dataset):
    def __init__(self, files: list[tuple[str, int]]):
        self.files = files

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, i: int):
        path, label = self.files[i]
        return to_tensor(Image.open(path)), label


def _collect() -> list[tuple[str, int]]:
    files: list[tuple[str, int]] = []
    for label, cls in enumerate(CLASSES):
        for p in glob.glob(os.path.join(DATA, cls, "*.png")):
            files.append((p, label))
    random.seed(7)
    random.shuffle(files)
    return files


def main(epochs: int = 8, batch: int = 32) -> None:
    files = _collect()
    if not files:
        raise SystemExit("No training data — run `python -m cv.generate_notes` first.")
    split = int(len(files) * 0.85)
    train_dl = DataLoader(NoteDataset(files[:split]), batch_size=batch, shuffle=True)
    val_dl = DataLoader(NoteDataset(files[split:]), batch_size=batch)

    torch.manual_seed(7)
    model = NoteCNN()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    for ep in range(epochs):
        model.train()
        for xb, yb in train_dl:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
        # val accuracy
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for xb, yb in val_dl:
                pred = model(xb).argmax(1)
                correct += (pred == yb).sum().item()
                total += len(yb)
        print(f"epoch {ep+1}/{epochs}  val_acc={correct/total:.3f}")

    torch.save(model.state_dict(), WEIGHTS)
    print(f"Saved {WEIGHTS}")


if __name__ == "__main__":
    main()
