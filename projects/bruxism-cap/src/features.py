from __future__ import annotations

import math
from typing import Iterable

import numpy as np

EEG_BANDS: dict[str, tuple[float, float]] = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 12.0),
    "beta": (12.0, 30.0),
}


def _as_array(signal: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(signal) if not isinstance(signal, np.ndarray) else signal, dtype=float)
    if arr.ndim != 1:
        raise ValueError("signal must be one-dimensional")
    if arr.size < 4:
        raise ValueError("signal must contain at least 4 samples")
    return arr


def root_mean_square(signal: Iterable[float]) -> float:
    arr = _as_array(signal)
    return float(np.sqrt(np.mean(arr ** 2)))


def zero_crossing_rate(signal: Iterable[float]) -> float:
    arr = _as_array(signal)
    centered = arr - np.mean(arr)
    crossings = np.sum(np.diff(np.signbit(centered)).astype(int))
    return float(crossings / max(len(arr) - 1, 1))


def line_length(signal: Iterable[float]) -> float:
    arr = _as_array(signal)
    return float(np.sum(np.abs(np.diff(arr))))


def sample_entropy(signal: Iterable[float], m: int = 2, r_ratio: float = 0.2) -> float:
    arr = _as_array(signal)
    sd = float(np.std(arr))
    if sd == 0.0:
        return 0.0
    r = r_ratio * sd

    def _phi(order: int) -> float:
        count = 0
        total = 0
        for i in range(len(arr) - order):
            template = arr[i : i + order]
            for j in range(i + 1, len(arr) - order + 1):
                candidate = arr[j : j + order]
                if np.max(np.abs(template - candidate)) <= r:
                    count += 1
                total += 1
        if total == 0:
            return 0.0
        return count / total

    phi_m = _phi(m)
    phi_m1 = _phi(m + 1)
    if phi_m == 0.0 or phi_m1 == 0.0:
        return 0.0
    return float(-math.log(phi_m1 / phi_m))


def bandpower_features(signal: Iterable[float], sfreq: float, bands: dict[str, tuple[float, float]] | None = None) -> dict[str, float]:
    arr = _as_array(signal)
    if sfreq <= 0:
        raise ValueError("sfreq must be positive")
    bands = bands or EEG_BANDS
    centered = arr - np.mean(arr)
    window = np.hanning(len(centered))
    spectrum = np.fft.rfft(centered * window)
    psd = (np.abs(spectrum) ** 2) / max(len(centered), 1)
    freqs = np.fft.rfftfreq(len(centered), d=1.0 / sfreq)
    total_power = float(np.sum(psd[(freqs >= 0.5) & (freqs <= 30.0)]))
    total_power = total_power if total_power > 0 else 1e-12

    features: dict[str, float] = {}
    for name, (low, high) in bands.items():
        mask = (freqs >= low) & (freqs < high)
        band_power = float(np.sum(psd[mask]))
        features[f"bp_{name}"] = band_power
        features[f"rel_bp_{name}"] = band_power / total_power
    return features


def extract_window_features(signal: Iterable[float], sfreq: float) -> dict[str, float]:
    arr = _as_array(signal)
    feats: dict[str, float] = {
        "n_samples": float(len(arr)),
        "duration_s": float(len(arr) / sfreq),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "ptp": float(np.ptp(arr)),
        "rms": root_mean_square(arr),
        "line_length": line_length(arr),
        "zero_crossing_rate": zero_crossing_rate(arr),
        "sample_entropy": sample_entropy(arr),
    }
    feats.update(bandpower_features(arr, sfreq))

    beta = feats.get("rel_bp_beta", 0.0)
    theta = feats.get("rel_bp_theta", 0.0)
    alpha = feats.get("rel_bp_alpha", 0.0)
    delta = feats.get("rel_bp_delta", 0.0)

    feats["ratio_theta_beta"] = theta / max(beta, 1e-12)
    feats["ratio_alpha_beta"] = alpha / max(beta, 1e-12)
    feats["ratio_alpha_delta"] = alpha / max(delta, 1e-12)
    return feats


def feature_column_order() -> list[str]:
    example = extract_window_features(np.sin(np.linspace(0, 2 * np.pi, 256)), sfreq=128.0)
    return list(example.keys())
