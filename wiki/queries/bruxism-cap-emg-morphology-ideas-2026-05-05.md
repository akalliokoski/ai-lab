---
title: Bruxism CAP EMG morphology ideas
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, experiment, evaluation, notes]
sources:
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
  - raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md
  - raw/articles/portable-emg-temporal-patterns-2026.md
  - raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md
  - raw/articles/portable-masseter-emg-validity-2019.md
---

# Bruxism CAP EMG morphology ideas

Question: after `pass33`, what compact literature-backed EMG morphology ideas still fit the current handcrafted CAP baseline?

## Repo-grounded answer

The strongest next move is still representation-focused rather than deletion-focused. The repaired percentile-band `A1-only` scaffold is now timing-matched across channels, and `pass33` preserved the sharpest negative result yet: removing `mean`, `min`, and `max` leaves `n3` high while collapsing `brux1`. That points away from another subtraction-first pass and toward better expression of the retained EMG morphology family. [[bruxism-cap]] [[bruxism-cap-emg-a1-raw-location-ablation-2026-05-05]] [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]]

## Most relevant ideas that fit now

### 1. Record-relative plus log-compressed amplitude-envelope representation
Best immediate fit.

Why: general sEMG literature supports compact log-energy / log-RMS style features, while the repo evidence suggests absolute amplitude still contains useful signal but is represented too rawly across subjects. A bounded rerun should add within-record robust z-score or percentile-rank versions of `rms`, `ptp`, `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, and `p95_abs`, plus log-compressed versions of `rms`, `envelope_mean`, and `p95_abs`. [[bruxism-cap]]

### 2. Shape-focused morphology features
Second-best fit.

Why: the current EMG gap is broader than one bad amplitude feature. The inspected Sensors 2024 note used compact higher-order statistics such as skewness, kurtosis, square integral, average energy, and temporal moment; broader sEMG recognition work also supports Hjorth parameters in small feature sets. Adding `skewness`, `kurtosis`, `hjorth_mobility`, and `hjorth_complexity` is a cheap way to test whether `brux1` and `brux2` differ from controls in waveform organization rather than only raw level. [[bruxism-cap]]

### 3. Better burst morphology from conditioned traces
Third fit.

Why: the sleep-bruxism ambulatory-EMG review emphasizes that thresholding and signal-processing differences heavily affect what counts as masticatory muscle activity. The current repo burst features are simple threshold summaries. A Teager-Kaiser-energy-conditioned trace plus compact burst duration / duty-cycle summaries could be a meaningful next family if the record-relative rerun fails. [[bruxism-cap]]

### 4. Compact EMG-specific spectral descriptors
Still plausible, but not first.

Why: the 2026 bruxism spectral pilot argues that frequency-spectrum descriptors may capture clinically meaningful variation missed by event/time indices. This does not overturn the repo's earlier spectral negatives, but it does caution against reading them as proof that all EMG spectrum is useless. If revisited, it should be as a compact EMG-specific median/mean-frequency family, not as a broad EEG-band package. [[bruxism-cap]]

## What does not fit now

- Do not switch away from CAP yet; recent literature did not reveal a clearly better open benchmark.
- Do not jump to a deep-model rewrite before testing one bounded representation fix.
- Do not pull in cross-channel correlation features yet; they would blur the current single-channel matched benchmark interpretation.

## One smallest next experiment

Keep the repaired percentile-band `A1-only` selector, labels, subject set, and `logreg` LOSO surface fixed. Add only record-relative and log-compressed versions of the retained amplitude-envelope family on `EMG1-EMG2`, then compare against `pass28` and `pass33` on `brux1 - n3`, best-bruxism-minus-highest-control margin, and subject-level sensitivity. [[bruxism-cap-emg-a1-percentile-band-rerun-2026-05-05]] [[bruxism-cap-emg-a1-raw-location-ablation-2026-05-05]]

## Artifact

Detailed repo report: `projects/bruxism-cap/reports/literature-emg-morphology-ideas-2026-05-05.md`
