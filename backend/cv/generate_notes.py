"""Synthetic Indian banknote generator (Component 2). Procedurally draws stylised
notes with the security features the brief names — denomination, serial number,
security thread, microprint band, UV-reactive patch.

GENUINE notes have all features intact; COUNTERFEIT notes degrade a random subset
(blurred/missing microprint, shifted/absent thread, wrong serial pattern, missing
UV patch). The CNN learns the difference; OpenCV checks explain it.

DISCLOSED SYNTHETIC — no real currency imagery is used. Run:
  python -m cv.generate_notes            # builds cv/data/{genuine,fake} + cv/samples
"""
from __future__ import annotations

import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(HERE, "samples")

W, H = 440, 200
THREAD_X = int(W * 0.62)
MICRO_BOX = (20, H - 38, W - 20, H - 18)   # microprint band
UV_BOX = (W - 90, 80, W - 50, 120)          # UV patch

# denomination -> base tint (RGB)
DENOMS = {
    "100": (205, 190, 225),
    "200": (240, 205, 150),
    "500": (190, 190, 178),
    "2000": (222, 170, 205),
}


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _genuine_serial() -> str:
    # RBI-style: 3 alphanumerics + space + 6 digits, e.g. "8AB 123456"
    head = f"{random.randint(0,9)}{random.choice('ABCDEFGHJKLMN')}{random.choice('ABCDEFGHJKLMN')}"
    return f"{head} {random.randint(0,999999):06d}"


def _fake_serial() -> str:
    # wrong format: random length / wrong grouping
    return "".join(random.choice("0123456789XYZ?") for _ in range(random.choice([5, 7, 9])))


def draw_note(denom: str, counterfeit: bool) -> Image.Image:
    tint = DENOMS[denom]
    img = Image.new("RGB", (W, H), tint)
    d = ImageDraw.Draw(img)

    # subtle guilloche-ish texture
    for _ in range(40):
        x0, y0 = random.randint(0, W), random.randint(0, H)
        d.arc([x0 - 30, y0 - 30, x0 + 30, y0 + 30],
              random.randint(0, 180), random.randint(180, 360),
              fill=tuple(max(0, c - 25) for c in tint))

    flaws = set()
    if counterfeit:
        flaws = set(random.sample(["micro", "thread", "serial", "uv", "blur"],
                                  k=random.randint(2, 4)))

    # denomination
    d.text((16, 12), denom, font=_font(46), fill=(30, 30, 30))
    d.text((W - 90, H - 50), denom, font=_font(34), fill=(40, 40, 40))
    d.text((16, 70), "RESERVE BANK OF INDIA", font=_font(13), fill=(50, 50, 50))

    # serial number
    serial = _fake_serial() if "serial" in flaws else _genuine_serial()
    d.text((W - 150, 10), serial, font=_font(15), fill=(20, 20, 20))
    d.text((20, H - 60), serial, font=_font(13), fill=(20, 20, 20))

    # security thread (vertical stripe)
    if "thread" not in flaws:
        tx = THREAD_X + (random.randint(40, 70) if "thread" in flaws else 0)
        for y in range(8, H - 8, 10):
            d.rectangle([tx, y, tx + 4, y + 6], fill=(120, 120, 140))

    # microprint band (tiny repeated text)
    if "micro" not in flaws:
        micro = (f"RBI {denom} " * 12)
        d.text((MICRO_BOX[0], MICRO_BOX[1]), micro, font=_font(9), fill=(35, 35, 35))

    # UV-reactive patch (bright cyan rectangle)
    if "uv" not in flaws:
        d.rectangle(UV_BOX, fill=(90, 230, 230))
        d.text((UV_BOX[0] + 4, UV_BOX[1] + 10), denom, font=_font(14), fill=(0, 70, 70))

    # localized degradations
    if "micro" in flaws:
        crop = img.crop(MICRO_BOX).filter(ImageFilter.GaussianBlur(3))
        img.paste(crop, MICRO_BOX[:2])
    if "blur" in flaws:
        img = img.filter(ImageFilter.GaussianBlur(0.8))

    return img


def _augment(img: Image.Image) -> Image.Image:
    img = img.rotate(random.uniform(-5, 5), expand=False, fillcolor=(200, 200, 200))
    arr = np.asarray(img).astype(np.float32)
    arr *= random.uniform(0.85, 1.15)                       # brightness
    arr += np.random.normal(0, random.uniform(2, 9), arr.shape)  # noise
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def ensure_samples() -> str:
    """Write just the curated demo samples (fast). Used lazily by the API so the
    sample picker works without building the full training set."""
    os.makedirs(SAMPLES, exist_ok=True)
    if not any(f.endswith(".png") for f in os.listdir(SAMPLES)):
        random.seed(7)
        for denom in DENOMS:
            draw_note(denom, False).save(os.path.join(SAMPLES, f"genuine_{denom}.png"))
            draw_note(denom, True).save(os.path.join(SAMPLES, f"fake_{denom}.png"))
    return SAMPLES


def main(n_per_class: int = 300) -> None:
    random.seed(7)
    np.random.seed(7)
    for cls in ("genuine", "fake"):
        os.makedirs(os.path.join(DATA, cls), exist_ok=True)
    os.makedirs(SAMPLES, exist_ok=True)

    for i in range(n_per_class):
        for cls, fake in (("genuine", False), ("fake", True)):
            denom = random.choice(list(DENOMS))
            img = _augment(draw_note(denom, counterfeit=fake))
            img.save(os.path.join(DATA, cls, f"{denom}_{i:04d}.png"))

    # a curated handful of clean samples for the demo picker
    for denom in DENOMS:
        draw_note(denom, False).save(os.path.join(SAMPLES, f"genuine_{denom}.png"))
        draw_note(denom, True).save(os.path.join(SAMPLES, f"fake_{denom}.png"))

    print(f"Wrote {n_per_class*2} training images to {DATA} and "
          f"{len(DENOMS)*2} samples to {SAMPLES}")


if __name__ == "__main__":
    main()
