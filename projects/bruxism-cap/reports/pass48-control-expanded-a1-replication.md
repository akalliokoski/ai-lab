# Pass 48 — final bounded 7-subject repaired-A1 control-expanded replication

Date: 2026-05-06
Status: completed final bounded replication on the repaired `A1-only` control-expanded scaffold.

## Exact contract held fixed
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A1-only`
- scaffold family: repaired percentile-band / time-aware record-relative event-subset surface
- train-time exclusions: unchanged base exclusions `['^bp_', '^rel_bp_', '^ratio_']` plus no-shape exclusions `['skewness', 'kurtosis', 'hjorth_mobility', 'hjorth_complexity']`
- kept event subset: `['evt_active_fraction', 'evt_burst_duration_median_s', 'evt_interburst_gap_median_s']`
- model/eval contract: `logreg` with LOSO subject-level reporting and uncertainty outputs
- exact subjects: `['brux1', 'brux2', 'n1', 'n2', 'n3', 'n5', 'n11']`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py`
- Full rebuilt A1 candidate pool: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_full_envelope_shape_control_expanded.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass48-emg-a1-pct10-90-control-expanded.json`
- Intermediate selected table: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_pct10_90_timepos10_shape_control_expanded.csv`
- Final expanded table: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_control_expanded.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json`
- Summary JSON: `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.json`
- Cross-family audit JSON/MD: `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.json`, `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.md`
- Summary memo: `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md`

## Row-count and contract checks
- full exclusive `A1-only` candidate rows by subject before percentile-band selection: `{'brux1': 27, 'brux2': 29, 'n1': 139, 'n11': 14, 'n2': 94, 'n3': 29, 'n5': 134}` | total `466`
- selector kept subjects: `['brux1', 'brux2', 'n1', 'n2', 'n3', 'n5', 'n11']`
- selector rows written: `70`
- selected rows by subject: `{'brux1': 10, 'brux2': 10, 'n1': 10, 'n11': 10, 'n2': 10, 'n3': 10, 'n5': 10}`
- final expanded table rows by subject: `{'brux1': 10, 'brux2': 10, 'n1': 10, 'n11': 10, 'n2': 10, 'n3': 10, 'n5': 10}` | total `70`
- record-relative features applied: `['mean', 'max', 'ptp', 'line_length', 'zero_crossing_rate', 'rectified_std', 'envelope_std', 'envelope_cv', 'rectified_mean', 'envelope_mean', 'p95_abs']`
- event merge keys: `['subject_id', 'start_s', 'end_s', 'window_index']`
- event null counts after merge: `{'evt_active_fraction': 0, 'evt_burst_duration_median_s': 0, 'evt_interburst_gap_median_s': 0}`

## Subject-level result vs pass47 and legacy pass42 A1 anchor
- balanced accuracy: pass42 `0.750` | pass47 `0.750` | pass48 `0.400`
- sensitivity: pass42 `0.500` | pass47 `0.500` | pass48 `0.000`
- specificity: pass42 `1.000` | pass47 `1.000` | pass48 `0.800`
- best-bruxism-minus-highest-control margin: pass42 `+0.339` | pass47 `+0.335` | pass48 `-0.302`
- highest control: pass47 `n5` `0.334` | pass48 `n2` `0.614`
- best bruxism subject: pass48 `brux2` `0.311`
- `brux2 - highest_control`: pass47 `-0.123` | pass48 `-0.302`
- exact sensitivity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 0, 'trials': 2, 'low': 0.0, 'high': 0.841886116991581}`
- exact specificity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 4, 'trials': 5, 'low': 0.2835820638819105, 'high': 0.9949492366205319}`
- subject Brier: `0.288`

Pass48 subject rows:
- `brux1` (bruxism): score `0.108` | predicted `control` | positive-window fraction `0.000` | windows `10`
- `brux2` (bruxism): score `0.311` | predicted `control` | positive-window fraction `0.100` | windows `10`
- `n1` (control): score `0.239` | predicted `control` | positive-window fraction `0.100` | windows `10`
- `n2` (control): score `0.614` | predicted `bruxism` | positive-window fraction `1.000` | windows `10`
- `n3` (control): score `0.427` | predicted `control` | positive-window fraction `0.400` | windows `10`
- `n5` (control): score `0.211` | predicted `control` | positive-window fraction `0.100` | windows `10`
- `n11` (control): score `0.287` | predicted `control` | positive-window fraction `0.200` | windows `10`

## Shared-subject deltas vs pass47
- `brux1` (bruxism): pass48 `0.108` vs pass47 `0.669` | delta `-0.561` | labels pass48 `control` / pass47 `bruxism`
- `brux2` (bruxism): pass48 `0.311` vs pass47 `0.212` | delta `+0.099` | labels pass48 `control` / pass47 `control`
- `n3` (control): pass48 `0.427` vs pass47 `0.081` | delta `+0.347` | labels pass48 `control` / pass47 `control`
- `n5` (control): pass48 `0.211` vs pass47 `0.334` | delta `-0.123` | labels pass48 `control` / pass47 `control`
- `n11` (control): pass48 `0.287` vs pass47 `0.283` | delta `+0.004` | labels pass48 `control` / pass47 `control`

## Shared-core deltas vs pass42
- `brux1` (bruxism): pass48 `0.108` vs pass42 `0.136` | delta `-0.029` | labels pass48 `control` / pass42 `control`
- `brux2` (bruxism): pass48 `0.311` vs pass42 `0.825` | delta `-0.513` | labels pass48 `control` / pass42 `bruxism`
- `n3` (control): pass48 `0.427` vs pass42 `0.155` | delta `+0.272` | labels pass48 `control` / pass42 `control`
- `n5` (control): pass48 `0.211` vs pass42 `0.199` | delta `+0.012` | labels pass48 `control` / pass42 `control`
- `n11` (control): pass48 `0.287` vs pass42 `0.486` | delta `-0.199` | labels pass48 `control` / pass42 `control`

## Final decision
- verdict: The repaired A1-only control-expanded replication does not clear the honest tiny-N benchmark bar strongly enough to justify more CAP passes: the headline remains capped, or one bruxism subject still trails the control ceiling, so the CAP benchmark should be treated as complete rather than extended further.
- recommendation: `close`
- final note: If this final repaired A1 replication still fails to produce a clear two-bruxism-subject separation above the control ceiling, the CAP benchmark should be closed as scientifically informative but exhausted for further bounded passes.
