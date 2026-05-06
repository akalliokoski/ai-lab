# Pass 46 — repaired cross-family one-feature `evt_bursts_per_episode_mean` add-back on the frozen pass42/pass45 scaffold

Date: 2026-05-05
Status: bounded one-feature add-back completed. This pass keeps the repaired selected rows, five-subject benchmark, `EMG1-EMG2`, threshold `0.5`, `logreg` LOSO contract, pass45 shape-drop exclusions, and the validated pass42 event trio fixed, and restores only `evt_bursts_per_episode_mean`.

## Why this is the smallest valid next test
- no selector rerun, no row regeneration, no scaffold rewrite, no family change, no channel change, and no model-family change
- frozen repaired A3 base table reused directly from pass44/pass45: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- pass45 contract preserved at train time: compact shape family still excluded: `skewness, kurtosis, hjorth_mobility, hjorth_complexity`
- fixed validated event trio preserved: `evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s`
- exactly one event feature restored by row-key merge: `evt_bursts_per_episode_mean`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass46_repaired_cross_family_evt_bursts_per_episode_addback.py`
- Pass46 merged feature table: `projects/bruxism-cap/data/window_features_pass46_emg_s2_mcap_a3_only_pct10_90_record_relative_shape_eventsubset_plus_evt_bursts_per_episode_mean.csv`
- Pass46 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json`
- Pass46 summary JSON: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.json`
- Pass46 summary memo: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md`
- Paired audit JSON: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.json`
- Paired audit memo: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md`

## Scaffold and merge checks
- pass42 repaired A1 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass45 repaired A3 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass46 repaired A3 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- unchanged base exclusions: `['^bp_', '^rel_bp_', '^ratio_']`
- retained pass45 shape-drop exclusions: `['skewness', 'kurtosis', 'hjorth_mobility', 'hjorth_complexity']`
- event features kept at train time: `['evt_active_fraction', 'evt_burst_duration_median_s', 'evt_interburst_gap_median_s', 'evt_bursts_per_episode_mean']`
- add-back merge keys: `['subject_id', 'start_s', 'end_s', 'window_index']`
- add-back null count after merge: `0`
- frozen row ids preserved: `True`

## Subject-level comparison against pass42 and pass45 anchors
- balanced accuracy: pass42 `0.750` | pass45 `0.750` | pass46 `0.750`
- sensitivity: pass42 `0.500` | pass45 `0.500` | pass46 `0.500`
- specificity: pass42 `1.000` | pass45 `1.000` | pass46 `1.000`
- best-bruxism-minus-highest-control margin: pass42 `+0.339` | pass45 `+0.295` | pass46 `+0.292`
- pass46 highest control: `n5` at `0.347`
- pass46 best bruxism subject: `brux1` at `0.639`
- pass46 exact sensitivity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}`
- pass46 exact specificity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}`
- pass46 subject Brier: `0.207`

Subject score rows:
- `brux1` (bruxism): pass42 `0.136` -> pass45 `0.641` -> pass46 `0.639` | delta pass46 vs pass45 `-0.002` | delta pass46 vs pass42 `+0.502` | labels pass42 `control` -> pass45 `bruxism` -> pass46 `bruxism`
- `brux2` (bruxism): pass42 `0.825` -> pass45 `0.178` -> pass46 `0.196` | delta pass46 vs pass45 `+0.018` | delta pass46 vs pass42 `-0.629` | labels pass42 `bruxism` -> pass45 `control` -> pass46 `control`
- `n3` (control): pass42 `0.155` -> pass45 `0.134` -> pass46 `0.131` | delta pass46 vs pass45 `-0.003` | delta pass46 vs pass42 `-0.024` | labels pass42 `control` -> pass45 `control` -> pass46 `control`
- `n5` (control): pass42 `0.199` -> pass45 `0.337` -> pass46 `0.347` | delta pass46 vs pass45 `+0.010` | delta pass46 vs pass42 `+0.148` | labels pass42 `control` -> pass45 `control` -> pass46 `control`
- `n11` (control): pass42 `0.486` -> pass45 `0.345` -> pass46 `0.345` | delta pass46 vs pass45 `-0.000` | delta pass46 vs pass42 `-0.141` | labels pass42 `control` -> pass45 `control` -> pass46 `control`

## Paired subject-surface comparison against pass45
- paired margin delta (pass46 - pass45): `-0.004`
- subject prediction flips: `[]`
- pass46 vs pass42 prediction flips: `['brux1: control -> bruxism', 'brux2: bruxism -> control']`

## Did `brux2` improve relative to the highest control?
- pass42 `brux2 - highest_control`: `+0.339`
- pass45 `brux2 - highest_control`: `-0.167`
- pass46 `brux2 - highest_control`: `-0.151`
- delta vs pass45: `+0.016`
- delta vs pass42: `-0.490`
- no control crossed threshold on pass46: `True`

## Verdict
the one-feature add-back is directionally useful on repaired A3 because brux2 improves relative to the highest control without reopening controls

## Safest next bounded step
Keep pass45 and pass46 side by side as the repaired A3 no-shape base and one-feature add-back variant, then run one bounded interpretation pass that compares whether the add-back meaningfully changes the pass42-vs-A3 subject split enough to justify preserving it as the new repaired A3 anchor.
