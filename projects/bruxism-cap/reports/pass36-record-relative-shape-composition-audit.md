# Pass 36 — record-relative plus compact shape composition audit on repaired `A1-only` EMG scaffold

Date: 2026-05-05
Status: bounded composition audit completed; added the four pass35 compact shape descriptors on top of the existing pass34 record-relative `EMG1-EMG2` percentile-band table while keeping selected rows, subject set, LOSO split, train-time exclusions, and model family fixed.

## Why this pass exists

This pass asks one exact follow-up question from the campaign handoff:
- start from the existing pass34 record-relative audit path and feature table
- keep the repaired five-subject percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed
- keep the same train-time exclusions fixed: `^bp_, ^rel_bp_, ^ratio_`
- keep the same `logreg` LOSO interpretation surface
- add only the same four compact shape features from pass35: `skewness, kurtosis, hjorth_mobility, hjorth_complexity`
- compare only pass34 versus `record-relative + shape`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass36_record_relative_shape_composition_audit.py`
- Composed feature table: `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`
- Summary JSON: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md`

## Scaffold parity checks
- pass34 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass35 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass36 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- warnings:
- none

## Honest LOSO subject-level comparison
- pass34 balanced accuracy: `0.500`
- pass36 balanced accuracy: `0.750`
- pass34 sensitivity: `0.000`
- pass36 sensitivity: `0.500`
- pass34 specificity: `1.000`
- pass36 specificity: `1.000`
- pass34 best-bruxism-minus-highest-control margin: `+0.041`
- pass36 best-bruxism-minus-highest-control margin: `+0.319`

Subject score deltas:
- `brux1`: pass34 `0.180` -> pass36 `0.112` (delta `-0.068`) | predicted `control` -> `control`
- `brux2`: pass34 `0.480` -> pass36 `0.808` (delta `+0.328`) | predicted `control` -> `bruxism`
- `n3`: pass34 `0.439` -> pass36 `0.068` (delta `-0.370`) | predicted `control` -> `control`
- `n5`: pass34 `0.379` -> pass36 `0.385` (delta `+0.006`) | predicted `control` -> `control`
- `n11`: pass34 `0.376` -> pass36 `0.489` (delta `+0.112`) | predicted `control` -> `control`

## Required gap checks
- pass34 `n3 - brux1` gap: `+0.259`
- pass36 `n3 - brux1` gap: `-0.043`
- pass34 `brux2 - n3` gap: `+0.041`
- pass36 `brux2 - n3` gap: `+0.740`
- pass34 best-bruxism-minus-highest-control margin: `+0.041`
- pass36 best-bruxism-minus-highest-control margin: `+0.319`

## Shape-aware gap contributors
Top positive contributors keeping `n3` above `brux1`:
  - `mean` contribution delta `+46.577` | z-mean delta `-655.647` | raw-mean delta `-0.783179`
  - `rectified_std` contribution delta `+3.803` | z-mean delta `-13.880` | raw-mean delta `-10.538216`
  - `envelope_cv` contribution delta `+1.422` | z-mean delta `-11.682` | raw-mean delta `-32.462936`
  - `p95_abs` contribution delta `+0.854` | z-mean delta `-4.196` | raw-mean delta `-6.312733`
  - `ptp` contribution delta `+0.831` | z-mean delta `-20.358` | raw-mean delta `-85.551894`
  - `kurtosis` contribution delta `+0.674` | z-mean delta `-1.626` | raw-mean delta `-27.241218`

Top negative contributors against `brux2` versus `n3`:
  - `hjorth_complexity` contribution delta `-0.612` | z-mean delta `+1.495` | raw-mean delta `+1.014378`
  - `skewness` contribution delta `-0.180` | z-mean delta `-0.273` | raw-mean delta `-0.307258`
  - `kurtosis` contribution delta `-0.143` | z-mean delta `+0.095` | raw-mean delta `+2.197268`
  - `p95_abs` contribution delta `-0.028` | z-mean delta `-0.177` | raw-mean delta `-0.920743`
  - `rectified_mean` contribution delta `-0.027` | z-mean delta `-0.100` | raw-mean delta `-0.208240`
  - `envelope_mean` contribution delta `-0.027` | z-mean delta `-0.100` | raw-mean delta `-0.207593`

## Verdict
The two best current EMG gains do compose into a subject-sensitivity improvement on this repaired scaffold: `brux2` crosses the subject threshold (`0.480` -> `0.808`) and `n3` drops sharply (`0.439` -> `0.068`), but `brux1` gets worse (`0.180` -> `0.112`), so the gain is real but not a clean across-bruxism fix.

## Interpretation
1. This is an apples-to-apples composition audit: the pass34 selected rows stay fixed and the only added information is the same bounded pass35 shape family.
2. The key decision question is whether stacking the two best EMG clues finally clears honest subject-level sensitivity or at least improves the pass34 subject-ordering surface without introducing row drift.
3. The composition does help, but only through `brux2`: it rises above threshold while `brux1` falls further below threshold, so this is a real but incomplete benchmark improvement rather than a clean all-subject EMG fix.
