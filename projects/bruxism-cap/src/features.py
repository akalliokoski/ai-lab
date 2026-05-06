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


def normalize_signal(signal: Iterable[float], mode: str = "none") -> np.ndarray:
    arr = _as_array(signal)
    if mode == "none":
        return arr.copy()
    if mode == "median_mad":
        center = float(np.median(arr))
        mad = float(np.median(np.abs(arr - center)))
        scale = 1.4826 * mad
        if not np.isfinite(scale) or scale <= 1e-12:
            scale = float(np.std(arr))
        if not np.isfinite(scale) or scale <= 1e-12:
            scale = 1.0
        return (arr - center) / scale
    raise ValueError(f"unsupported normalize mode: {mode}")


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


def skewness(signal: Iterable[float]) -> float:
    arr = _as_array(signal)
    centered = arr - np.mean(arr)
    scale = float(np.std(centered))
    if not np.isfinite(scale) or scale <= 1e-12:
        return 0.0
    standardized = centered / scale
    return float(np.mean(standardized ** 3))


def kurtosis(signal: Iterable[float]) -> float:
    arr = _as_array(signal)
    centered = arr - np.mean(arr)
    scale = float(np.std(centered))
    if not np.isfinite(scale) or scale <= 1e-12:
        return 0.0
    standardized = centered / scale
    return float(np.mean(standardized ** 4) - 3.0)


def hjorth_parameters(signal: Iterable[float]) -> tuple[float, float]:
    arr = _as_array(signal)
    first_diff = np.diff(arr)
    second_diff = np.diff(first_diff)

    activity = float(np.var(arr))
    first_var = float(np.var(first_diff)) if first_diff.size else 0.0
    second_var = float(np.var(second_diff)) if second_diff.size else 0.0

    if not np.isfinite(activity) or activity <= 1e-12:
        return 0.0, 0.0
    mobility = float(np.sqrt(first_var / activity)) if first_var > 0 else 0.0
    if not np.isfinite(mobility) or mobility <= 1e-12 or first_var <= 1e-12 or second_var <= 1e-12:
        return mobility, 0.0
    complexity = float(np.sqrt(second_var / first_var) / mobility)
    if not np.isfinite(complexity):
        complexity = 0.0
    return mobility, complexity


def sample_entropy(
    signal: Iterable[float],
    m: int = 2,
    r_ratio: float = 0.2,
    max_points: int = 400,
) -> float:
    arr = _as_array(signal)
    if len(arr) > max_points:
        step = max(1, len(arr) // max_points)
        arr = arr[::step][:max_points]
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


def emg_envelope_features(signal: Iterable[float], sfreq: float) -> dict[str, float]:
    arr = _as_array(signal)
    if sfreq <= 0:
        raise ValueError("sfreq must be positive")

    rectified = np.abs(arr - np.mean(arr))
    smooth_samples = max(1, int(round(0.2 * sfreq)))
    kernel = np.ones(smooth_samples, dtype=float) / smooth_samples
    envelope = np.convolve(rectified, kernel, mode="same")

    rectified_mean = float(np.mean(rectified))
    rectified_std = float(np.std(rectified))
    envelope_mean = float(np.mean(envelope))
    envelope_std = float(np.std(envelope))
    burst_threshold = rectified_mean + rectified_std
    burst_mask = rectified >= burst_threshold
    burst_starts = np.logical_and(burst_mask, np.concatenate(([True], ~burst_mask[:-1])))
    burst_count = int(np.sum(burst_starts))
    duration_s = len(arr) / sfreq

    return {
        "rectified_mean": rectified_mean,
        "rectified_std": rectified_std,
        "envelope_mean": envelope_mean,
        "envelope_std": envelope_std,
        "envelope_cv": envelope_std / max(envelope_mean, 1e-12),
        "burst_fraction": float(np.mean(burst_mask.astype(float))),
        "burst_rate_hz": float(burst_count / max(duration_s, 1e-12)),
        "p95_abs": float(np.percentile(rectified, 95)),
    }


def centered_rectified_signal(signal: Iterable[float]) -> np.ndarray:
    arr = _as_array(signal)
    return np.abs(arr - np.mean(arr))


def robust_rectified_reference(signal: Iterable[float], *, floor: float = 1e-6) -> dict[str, float]:
    rectified = centered_rectified_signal(signal)
    median_rectified = float(np.median(rectified))
    mad_rectified = float(np.median(np.abs(rectified - median_rectified)))
    threshold = max(2.0 * median_rectified, median_rectified + 2.0 * mad_rectified, floor)
    return {
        "median_rectified": median_rectified,
        "mad_rectified": mad_rectified,
        "active_threshold": float(threshold),
    }


def _true_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    if mask.ndim != 1:
        raise ValueError("mask must be one-dimensional")
    if mask.size == 0:
        return []
    padded = np.concatenate(([False], mask.astype(bool), [False]))
    changes = np.diff(padded.astype(int))
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    return [(int(start), int(end)) for start, end in zip(starts, ends, strict=True)]


def emg_event_block_features(
    signal: Iterable[float],
    sfreq: float,
    *,
    reference_rectified_median: float | None = None,
    reference_rectified_mad: float | None = None,
    threshold_floor: float = 1e-6,
    min_burst_s: float = 0.25,
    merge_gap_s: float = 0.08,
    max_episode_gap_s: float = 3.0,
) -> dict[str, float]:
    arr = _as_array(signal)
    if sfreq <= 0:
        raise ValueError("sfreq must be positive")

    rectified = centered_rectified_signal(arr)
    if reference_rectified_median is None or reference_rectified_mad is None:
        reference = robust_rectified_reference(arr, floor=threshold_floor)
        reference_rectified_median = reference["median_rectified"]
        reference_rectified_mad = reference["mad_rectified"]
    threshold = max(
        2.0 * float(reference_rectified_median),
        float(reference_rectified_median) + 2.0 * float(reference_rectified_mad),
        threshold_floor,
    )

    active_mask = rectified >= threshold
    merged_mask = active_mask.copy()
    max_gap_samples = max(0, int(round(merge_gap_s * sfreq)))
    if max_gap_samples > 0:
        runs = _true_runs(active_mask)
        for (_, prev_end), (next_start, _) in zip(runs, runs[1:], strict=False):
            gap = next_start - prev_end
            if 0 < gap <= max_gap_samples:
                merged_mask[prev_end:next_start] = True

    min_burst_samples = max(1, int(round(min_burst_s * sfreq)))
    burst_runs = [run for run in _true_runs(merged_mask) if run[1] - run[0] >= min_burst_samples]
    burst_durations = [(end - start) / sfreq for start, end in burst_runs]

    if not burst_runs:
        return {
            "evt_burst_count_30s": 0.0,
            "evt_episode_count_30s": 0.0,
            "evt_bursts_per_episode_mean": 0.0,
            "evt_active_fraction": 0.0,
            "evt_burst_duration_median_s": 0.0,
            "evt_interburst_gap_median_s": float(max_episode_gap_s),
            "evt_phasic_like_episode_fraction": 0.0,
        }

    max_episode_gap_samples = max(1, int(round(max_episode_gap_s * sfreq)))
    episodes: list[list[tuple[int, int]]] = []
    current_episode = [burst_runs[0]]
    for burst in burst_runs[1:]:
        prev_end = current_episode[-1][1]
        gap_samples = burst[0] - prev_end
        if gap_samples < max_episode_gap_samples:
            current_episode.append(burst)
        else:
            episodes.append(current_episode)
            current_episode = [burst]
    episodes.append(current_episode)

    interburst_gaps_s: list[float] = []
    phasic_like_count = 0
    for episode in episodes:
        episode_durations = [(end - start) / sfreq for start, end in episode]
        interburst_gaps_s.extend([(episode[i + 1][0] - episode[i][1]) / sfreq for i in range(len(episode) - 1)])
        phasic_like = len(episode) >= 3 and all(min_burst_s <= duration <= 2.0 for duration in episode_durations)
        if phasic_like:
            phasic_like_count += 1

    active_samples = float(sum(end - start for start, end in burst_runs))
    return {
        "evt_burst_count_30s": float(len(burst_runs)),
        "evt_episode_count_30s": float(len(episodes)),
        "evt_bursts_per_episode_mean": float(len(burst_runs) / max(len(episodes), 1)),
        "evt_active_fraction": float(active_samples / len(arr)),
        "evt_burst_duration_median_s": float(np.median(burst_durations)),
        "evt_interburst_gap_median_s": float(np.median(interburst_gaps_s)) if interburst_gaps_s else float(max_episode_gap_s),
        "evt_phasic_like_episode_fraction": float(phasic_like_count / max(len(episodes), 1)),
    }


def extract_window_features(signal: Iterable[float], sfreq: float, normalize_mode: str = "none") -> dict[str, float]:
    arr = normalize_signal(signal, mode=normalize_mode)
    hjorth_mobility, hjorth_complexity = hjorth_parameters(arr)
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
        "skewness": skewness(arr),
        "kurtosis": kurtosis(arr),
        "hjorth_mobility": hjorth_mobility,
        "hjorth_complexity": hjorth_complexity,
    }
    feats.update(bandpower_features(arr, sfreq))
    feats.update(emg_envelope_features(arr, sfreq))

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
