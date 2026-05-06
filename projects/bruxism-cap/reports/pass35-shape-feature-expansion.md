# Pass 35 — compact shape-feature expansion on repaired `A1-only` EMG percentile-band scaffold

Date: 2026-05-05
Status: bounded representation rerun completed; rebuilt the same exclusive `SLEEP-S2 + MCAP-A1-only` EMG scaffold with four added shape descriptors (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) while keeping selector settings, subject set, and `logreg` LOSO fixed.

## Why this pass exists

Pass34 showed that within-record feature-space normalization improved `brux2` but still left `brux1` below `n3`, so the next bounded backup experiment from the synthesis memo was one compact shape-only family on the same repaired scaffold.

This pass makes exactly one primary increment:
- rebuild the uncapped exclusive `A1-only` `EMG1-EMG2` pool from raw EDF windows using the same extraction rule as pass27/pass28
- reapply the same repaired percentile-band selector from pass28 (`0.10` to `0.90`, `10` windows per subject)
- keep train-time exclusions fixed: `^bp_, ^rel_bp_, ^ratio_`
- keep the same `logreg` LOSO interpretation surface
- add only `skewness, kurtosis, hjorth_mobility, hjorth_complexity` to the feature table

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass35_shape_feature_expansion.py`
- Feature patch: `projects/bruxism-cap/src/features.py`
- Full rebuilt EMG pool: `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_full_envelope_shape.csv`
- Percentile-band selected dataset: `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv`
- Selector summary: `projects/bruxism-cap/reports/time-position-match-pass35-emg-a1-pct10-90-shape.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass35-emg-a1-pct10-90-shape.json`
- Summary JSON: `projects/bruxism-cap/reports/pass35-shape-feature-expansion-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass35-shape-feature-expansion.md`

## Anchor comparison path
- pass28 anchor LOSO report: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- pass34 mixed-result summary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass34-record-relative-emg-audit-summary.json`
- pass35 summary JSON: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass35-shape-feature-expansion-summary.json`

## Reproducibility and scaffold checks
- full-count check versus pass27 expectation: `{'brux1': 27, 'brux2': 29, 'n3': 29, 'n5': 134, 'n11': 14}`
- selected-count check versus pass28 expectation: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- selector mode: `percentile-band` with percentile band `{'lower_quantile': 0.1, 'upper_quantile': 0.9}`
- warnings:
- none

## Honest LOSO results
### Window level (`logreg`)
- balanced accuracy: `0.600`
- sensitivity: `0.080`
- specificity: `0.520`
- AUROC: `None`

### Subject level (`logreg`)
- baseline pass28 balanced accuracy: `0.333`
- pass35 balanced accuracy: `0.500`
- baseline pass28 sensitivity: `0.000`
- pass35 sensitivity: `0.000`
- baseline pass28 specificity: `0.667`
- pass35 specificity: `1.000`
- baseline best-bruxism-minus-highest-control margin: `-0.260`
- pass35 best-bruxism-minus-highest-control margin: `+0.012`

Subject score deltas:
- `brux1`: baseline `0.270` -> pass35 `0.216` (delta `-0.053`) | predicted `control` -> `control`
- `brux2`: baseline `0.036` -> pass35 `0.399` (delta `+0.363`) | predicted `control` -> `control`
- `n3`: baseline `0.530` -> pass35 `0.225` (delta `-0.305`) | predicted `bruxism` -> `control`
- `n5`: baseline `0.291` -> pass35 `0.387` (delta `+0.096`) | predicted `control` -> `control`
- `n11`: baseline `0.325` -> pass35 `0.188` (delta `-0.137`) | predicted `control` -> `control`

## Shape-feature focused checks
- pass28 `n3 - brux1` gap: `+0.260`
- pass35 `n3 - brux1` gap: `+0.009`
- pass28 `brux2 - n3` gap: `-0.494`
- pass35 `brux2 - n3` gap: `+0.174`

Top positive contributors keeping `n3` above `brux1`:
  - `kurtosis` contribution delta `+0.316` | z-mean delta `-1.626` | raw-mean delta `-27.241218`

Top negative contributors against `brux2` versus `n3`:
  - `skewness` contribution delta `-0.128` | z-mean delta `-0.273` | raw-mean delta `-0.307258`
  - `kurtosis` contribution delta `-0.062` | z-mean delta `+0.095` | raw-mean delta `+2.197268`

## Interpretation
1. This pass changes extraction only enough to regenerate the feature table with four bounded shape descriptors; the percentile-band row selection and LOSO evaluation surface remain the same repaired scaffold.
2. The main decision question is whether the added shape family moves `brux1` and/or `brux2` above the strongest controls without hiding subject-subset drift.
3. Treat this as a clean backup-branch test against pass28, with pass34 preserved as the intermediate mixed-result representation anchor rather than overwritten.
