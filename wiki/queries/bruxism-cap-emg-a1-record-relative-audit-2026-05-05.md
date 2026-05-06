---
title: Bruxism CAP EMG A1 record-relative audit (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md
  - queries/bruxism-cap-emg-within-record-normalization-ideas-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
On the repaired `SLEEP-S2 + MCAP-A1-only` percentile-band EMG scaffold, does one post-extraction within-record robust normalization audit improve the honest subject-level benchmark enough to beat the current anchor?

# Short answer
Only partially. The record-relative transform removes the worst control false positive and strongly improves `brux2`, but it does not rescue `brux1` and still leaves subject-level sensitivity at `0.000`.

Relative to pass28, subject-level balanced accuracy improves from `0.333` to `0.500`, `n3` drops below threshold (`0.530` -> `0.439`), and the best-bruxism-minus-highest-control margin flips from `-0.260` to `+0.041`. But that gain comes almost entirely from `brux2` rising from `0.036` to `0.480`; `brux1` actually falls from `0.270` to `0.180`, so the hardest subject/control overlap remains unresolved. [[bruxism-cap]] [[bruxism-cap-emg-within-record-normalization-ideas-2026-05-05]]

# What changed
This was the smallest representation-first test proposed by the pass34 synthesis:
- start from the existing pass28 `EMG1-EMG2` feature table
- keep row selection, subject set, and `logreg` LOSO fixed
- keep the existing `^bp_`, `^rel_bp_`, and `^ratio_` exclusions fixed
- replace only one retained feature subset with within-record robust relative values using `(x - median) / max(MAD, eps)`

Applied feature subset:
- `mean`
- `max`
- `ptp`
- `line_length`
- `zero_crossing_rate`
- `rectified_std`
- `envelope_std`
- `envelope_cv`
- `rectified_mean`
- `envelope_mean`
- `p95_abs`

Unchanged retained features:
- `std`
- `min`
- `rms`
- `sample_entropy`
- `burst_fraction`
- `burst_rate_hz`

# Key evidence
## Subject-level benchmark
- balanced accuracy: `0.333` -> `0.500`
- sensitivity: `0.000` -> `0.000`
- specificity: `0.667` -> `1.000`
- best-bruxism-minus-highest-control margin: `-0.260` -> `+0.041`

## Subject score shifts
- `brux1`: `0.270` -> `0.180`
- `brux2`: `0.036` -> `0.480`
- `n3`: `0.530` -> `0.439`
- `n5`: `0.291` -> `0.379`
- `n11`: `0.325` -> `0.376`

## Anchor-focused gaps
- `n3 - brux1`: `+0.260` -> `+0.259`
- `brux2 - n3`: `-0.494` -> `+0.041`

So the transform fixes the `brux2` versus `n3` reversal much more than it fixes the deeper `brux1` versus `n3` failure.^[../projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md]

# Verdict
Preserve pass34 as a mixed but useful result, not a new honest win. It shows that within-record feature-space normalization was the right smallest representation test to run, because it removes the worst control false positive and improves the overall margin without touching extraction. But it still fails the main subject-level criterion because `brux1` remains below threshold and below `n3`.

# Best next bounded step
Do not stack more normalization variants onto this pass immediately. Use this result to justify the backup branch from the synthesis memo: add one compact shape-focused family (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) on the same repaired scaffold, without combining it with further normalization or model changes.
