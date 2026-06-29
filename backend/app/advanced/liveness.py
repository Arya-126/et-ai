"""Deepfake-rejection via rPPG liveness. A real human face on camera shows a tiny
periodic colour change as blood pulses (remote photoplethysmography). A deepfake
overlay / digital puppet does not. We extract the green-channel signal over the
face ROI across frames, band-pass to the human heart-rate band (0.7–4 Hz ≈
42–240 bpm), and look for a dominant physiological peak.

`analyze_video(bytes)` runs the real pipeline on an uploaded clip (OpenCV).
`demo(live)` runs the SAME signal analysis on a disclosed synthetic rPPG signal,
so the algorithm is demonstrable without a camera.

Audio-visual desync detection (lip/phoneme vs audio) is the wired-in extension
point — it needs paired AV models/datasets beyond this build and is NOT faked.
"""
from __future__ import annotations

import logging
import math

import numpy as np

log = logging.getLogger("advanced.liveness")
LOW_HZ, HIGH_HZ = 0.7, 4.0


def _pulse_score(signal: np.ndarray, fps: float) -> dict:
    """Core rPPG analysis: detrend → FFT → power in the heart-rate band vs total."""
    x = np.asarray(signal, dtype=float)
    n = len(x)
    if n < 16 or fps <= 0:
        return {"live": False, "bpm": None, "snr": 0.0, "confidence": 0.0}
    x = x - np.mean(x)
    # linear detrend
    t = np.arange(n)
    if np.std(x) > 0:
        a, b = np.polyfit(t, x, 1)
        x = x - (a * t + b)
    x = x * np.hanning(n)

    freqs = np.fft.rfftfreq(n, d=1.0 / fps)
    power = np.abs(np.fft.rfft(x)) ** 2
    band = (freqs >= LOW_HZ) & (freqs <= HIGH_HZ)
    if not band.any() or power.sum() == 0:
        return {"live": False, "bpm": None, "snr": 0.0, "confidence": 0.0}

    band_power = power[band]
    peak_i = np.argmax(band_power)
    peak_freq = freqs[band][peak_i]
    peak_pwr = band_power[peak_i]
    # SNR: peak vs mean of the rest of the band
    rest = np.delete(band_power, peak_i)
    snr = float(peak_pwr / (np.mean(rest) + 1e-9))
    in_band_ratio = float(band_power.sum() / power.sum())

    live = snr >= 4.0 and in_band_ratio >= 0.30
    confidence = max(0.0, min(1.0, (snr / 12.0) * 0.6 + in_band_ratio * 0.4))
    return {
        "live": bool(live),
        "bpm": round(float(peak_freq * 60), 1),
        "snr": round(snr, 2),
        "in_band_ratio": round(in_band_ratio, 2),
        "confidence": round(confidence, 2),
    }


def available() -> bool:
    try:
        import cv2  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


def analyze_video(video_bytes: bytes) -> dict | None:
    """Real path: extract the green-channel face signal from an uploaded clip."""
    try:
        import os
        import tempfile

        import cv2
    except Exception as exc:  # noqa: BLE001
        log.info("liveness unavailable (%s)", exc)
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    try:
        tmp.write(video_bytes)
        tmp.close()
        cap = cv2.VideoCapture(tmp.name)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        greens: list[float] = []
        frames = 0
        while frames < 300:
            ok, frame = cap.read()
            if not ok:
                break
            frames += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.2, 5)
            if len(faces):
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                roi = frame[y:y + h, x:x + w]
            else:
                H, W = frame.shape[:2]
                roi = frame[H // 4:3 * H // 4, W // 4:3 * W // 4]
            greens.append(float(np.mean(roi[:, :, 1])))   # green channel
        cap.release()
        if len(greens) < 16:
            return {"verdict": "INSUFFICIENT", "detail": "Too few frames / no face found.",
                    **_pulse_score(np.array(greens or [0.0]), fps)}
        res = _pulse_score(np.array(greens), fps)
        res["verdict"] = "LIVE" if res["live"] else "SPOOF / DEEPFAKE"
        res["frames"] = frames
        return res
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def demo(live: bool, fps: float = 30.0, seconds: float = 6.0) -> dict:
    """Run the real analysis on a disclosed synthetic rPPG signal."""
    n = int(fps * seconds)
    t = np.arange(n) / fps
    rng = np.random.default_rng(7 if live else 13)
    if live:
        bpm = 72.0
        sig = 1.5 * np.sin(2 * math.pi * (bpm / 60) * t) + rng.normal(0, 0.6, n)
        sig += 0.4 * np.sin(2 * math.pi * 0.25 * t)        # slow respiration drift
    else:
        # deepfake overlay: no physiological pulse — just sensor noise + compression flicker
        sig = rng.normal(0, 1.0, n) + 0.2 * np.sin(2 * math.pi * 8.0 * t)
    res = _pulse_score(sig, fps)
    res["verdict"] = "LIVE" if res["live"] else "SPOOF / DEEPFAKE"
    res["source"] = "synthetic rPPG signal (disclosed)"
    return res
