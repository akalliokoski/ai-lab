# Pass 45 — repaired A3 same-table shape-block ablation

Date: 2026-05-05
Status: bounded same-table ablation completed. This pass reuses the frozen pass44 repaired `A3-only` table, keeps the five-subject benchmark, `EMG1-EMG2`, the fixed 3-feature event trio, train-time exclusions, threshold `0.5`, and `logreg` LOSO contract unchanged, and drops only the compact shape family at train time.

## Why this is the smallest valid test
- no selector rerun, no new row generation, no family change, no channel change, no model-family change, and no event-subset change
- input table reused directly: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- only additional train-time removals are the four compact shape features: `skewness, kurtosis, hjorth_mobility, hjorth_complexity`
- this isolates whether existing secondary shape support on the repaired pass44 table is suppressing `brux2` without reopening the stronger amplitude / dispersion carrier or the validated event trio

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass45_repaired_a3_shape_block_ablation.py`
- Reused repaired pass44 table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- Pass45 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json`
- Pass45 summary JSON: `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.json`
- Pass45 summary memo: `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md`
- Paired audit JSON: `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.json`
- Paired audit memo: `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md`

## Scaffold parity checks
- pass42 repaired A1 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass44 repaired A3 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass45 repaired A3 no-shape counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- unchanged base exclusions: `['^bp_', '^rel_bp_', '^ratio_']`
- added shape-drop exclusions: `['skewness', 'kurtosis', 'hjorth_mobility', 'hjorth_complexity']`
- shape features still present in the reused table before exclusion: `{'skewness': True, 'kurtosis': True, 'hjorth_mobility': True, 'hjorth_complexity': True}`

## Subject-level comparison against pass42 and pass44
- balanced accuracy: pass42 `0.750` | pass44 `0.750` | pass45 `0.750`
- sensitivity: pass42 `0.500` | pass44 `0.500` | pass45 `0.500`
- specificity: pass42 `1.000` | pass44 `1.000` | pass45 `1.000`
- best-bruxism-minus-highest-control margin: pass42 `+0.339` | pass44 `+0.138` | pass45 `+0.295`
- pass45 highest control: `n11` at `0.345`
- pass45 exact sensitivity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}`
- pass45 exact specificity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}`
- pass45 subject Brier: `0.211`

Subject score rows:
- `brux1` (bruxism): pass42 `0.136` -> pass44 `0.532` -> pass45 `0.641` | delta pass45 vs pass44 `+0.109` | delta pass45 vs pass42 `+0.504` | labels pass42 `control` -> pass44 `bruxism` -> pass45 `bruxism`
- `brux2` (bruxism): pass42 `0.825` -> pass44 `0.123` -> pass45 `0.178` | delta pass45 vs pass44 `+0.055` | delta pass45 vs pass42 `-0.646` | labels pass42 `bruxism` -> pass44 `control` -> pass45 `control`
- `n3` (control): pass42 `0.155` -> pass44 `0.034` -> pass45 `0.134` | delta pass45 vs pass44 `+0.100` | delta pass45 vs pass42 `-0.022` | labels pass42 `control` -> pass44 `control` -> pass45 `control`
- `n5` (control): pass42 `0.199` -> pass44 `0.365` -> pass45 `0.337` | delta pass45 vs pass44 `-0.028` | delta pass45 vs pass42 `+0.138` | labels pass42 `control` -> pass44 `control` -> pass45 `control`
- `n11` (control): pass42 `0.486` -> pass44 `0.395` -> pass45 `0.345` | delta pass45 vs pass44 `-0.049` | delta pass45 vs pass42 `-0.141` | labels pass42 `control` -> pass44 `control` -> pass45 `control`

## Subject prediction flips
- pass45 vs pass44: `[]`
- pass45 vs pass42: `['brux1: control -> bruxism', 'brux2: bruxism -> control']`

## Verdict
- `brux2` delta vs pass44: `+0.055`
- `brux1` delta vs pass44: `+0.109`
- no control crossed threshold on pass45: `True`
- smallest-test verdict: shape-family removal looks directionally useful and should be preserved as the new repaired A3 working point

## Safest next step
Keep the repaired pass45 no-shape table as the new A3 anchor and run the already-preserved paired subject-surface audit against pass42 before considering the backup one-feature event add-back.
