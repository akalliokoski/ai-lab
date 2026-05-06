# Pass 34 — record-relative robust feature-space normalization audit on repaired `A1-only` EMG

Date: 2026-05-05
Status: bounded representation audit completed; one post-extraction feature-table transform tested the retained `EMG1-EMG2` morphology-envelope family without changing selector rules, labels, subject set, or model family.

## Why this is the smallest valid test

This pass implements exactly one representation change from the pass34 synthesis memo:
- start from the existing pass28 `EMG1-EMG2` feature CSV
- keep the repaired `SLEEP-S2 + MCAP-A1-only` percentile-band selected rows fixed
- keep the same train-time exclusions fixed: `^bp_, ^rel_bp_, ^ratio_`
- keep the same model family fixed: `logreg` LOSO
- replace only a bounded retained feature subset with within-record robust relative values using `(x - median_subject_feature) / max(MAD_subject_feature, 1e-06)`

## What changed

Transformed retained features:
- `mean, max, ptp, line_length, zero_crossing_rate, rectified_std, envelope_std, envelope_cv, rectified_mean, envelope_mean, p95_abs`

Intentionally left unchanged:
- window extraction and selector logic
- non-transformed retained features (`std`, `min`, `rms`, `sample_entropy`, `burst_fraction`, `burst_rate_hz`)
- model family, thresholding surface, and subject set
- all `bp_`, `rel_bp_`, and `ratio_` exclusions from the anchor

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`
- Transformed feature table: `projects/bruxism-cap/data/window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass34-emg-a1-pct10-90-record-relative.json`
- Summary JSON: `projects/bruxism-cap/reports/pass34-record-relative-emg-audit-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md`

## Honest LOSO subject-level comparison
- baseline subject-level balanced accuracy: `0.333`
- relative subject-level balanced accuracy: `0.500`
- baseline subject-level sensitivity: `0.000`
- relative subject-level sensitivity: `0.000`
- baseline best-bruxism-minus-highest-control margin: `-0.260`
- relative best-bruxism-minus-highest-control margin: `+0.041`

Subject score deltas:
- `brux1`: baseline `0.270` -> relative `0.180` (delta `-0.090`) | predicted `control` -> `control`
- `brux2`: baseline `0.036` -> relative `0.480` (delta `+0.444`) | predicted `control` -> `control`
- `n3`: baseline `0.530` -> relative `0.439` (delta `-0.091`) | predicted `bruxism` -> `control`
- `n5`: baseline `0.291` -> relative `0.379` (delta `+0.088`) | predicted `control` -> `control`
- `n11`: baseline `0.325` -> relative `0.376` (delta `+0.051`) | predicted `control` -> `control`

## Anchor-focused score checks
- baseline `n3 - brux1` gap: `+0.260`
- relative `n3 - brux1` gap: `+0.259`
- baseline `brux2 - n3` gap: `-0.494`
- relative `brux2 - n3` gap: `+0.041`
- baseline best-bruxism-minus-highest-control margin: `-0.260`
- relative best-bruxism-minus-highest-control margin: `+0.041`

## Interpretation

1. This was a pure post-extraction audit: the selector scaffold stayed fixed, so any movement is attributable to one within-record robust representation change rather than extraction drift.
2. The key decision target is whether `brux1` moves closer to or above `n3` without collapsing `brux2` or inflating controls.
3. Regardless of outcome, this pass preserves an auditable anchor comparison because only one bounded feature-family transform changed and the unchanged retained features remain visible.

## What was intentionally left for later

- no broad waveform-level normalization rewrite
- no backup shape-family expansion (`skewness`, `kurtosis`, Hjorth features)
- no train-time include/exclude rewrite beyond the existing anchor exclusions
- no `C4-P4` comparison rerun in this pass
