# Pass 47 — first bounded 7-subject repaired-A3 control-expanded rerun

Date: 2026-05-06
Status: completed exact 7-subject control-expanded rerun on the frozen repaired `A3-only` no-shape contract.

## Exact contract held fixed
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A3-only`
- scaffold family: repaired percentile-band / time-aware record-relative event-subset surface
- train-time exclusions: unchanged base exclusions `['^bp_', '^rel_bp_', '^ratio_']` plus pass45 shape-drop exclusions `['skewness', 'kurtosis', 'hjorth_mobility', 'hjorth_complexity']`
- kept event subset: `['evt_active_fraction', 'evt_burst_duration_median_s', 'evt_interburst_gap_median_s']`
- model/eval contract: `logreg` with LOSO subject-level reporting and uncertainty outputs
- exact subjects: `['brux1', 'brux2', 'n1', 'n2', 'n3', 'n5', 'n11']`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass47_control_expanded_rerun.py`
- Full rebuilt A3 candidate pool: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_full_envelope_shape_control_expanded.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass47-emg-a3-pct10-90-control-expanded.json`
- Intermediate selected table: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_pct10_90_timepos10_shape_control_expanded.csv`
- Final expanded table: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_control_expanded.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-control-expanded.json`
- Summary JSON: `projects/bruxism-cap/reports/pass47-control-expanded-rerun.json`
- Paired pass45 audit JSON/MD: `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.json`, `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md`
- Paired pass46 audit JSON/MD: `projects/bruxism-cap/reports/pass47-vs-pass46-paired-subject-surface-audit.json`, `projects/bruxism-cap/reports/pass47-vs-pass46-paired-subject-surface-audit.md`
- Summary memo: `projects/bruxism-cap/reports/pass47-control-expanded-rerun.md`

## Row-count and contract checks
- full exclusive `A3-only` candidate rows by subject before percentile-band selection: `{'brux1': 31, 'brux2': 111, 'n1': 56, 'n11': 42, 'n2': 49, 'n3': 76, 'n5': 38}` | total `403`
- selector kept subjects: `['brux1', 'brux2', 'n1', 'n2', 'n3', 'n5', 'n11']`
- selector rows written: `70`
- selected rows by subject: `{'brux1': 10, 'brux2': 10, 'n1': 10, 'n11': 10, 'n2': 10, 'n3': 10, 'n5': 10}`
- final expanded table rows by subject: `{'brux1': 10, 'brux2': 10, 'n1': 10, 'n11': 10, 'n2': 10, 'n3': 10, 'n5': 10}` | total `70`
- record-relative features applied: `['mean', 'max', 'ptp', 'line_length', 'zero_crossing_rate', 'rectified_std', 'envelope_std', 'envelope_cv', 'rectified_mean', 'envelope_mean', 'p95_abs']`
- event merge keys: `['subject_id', 'start_s', 'end_s', 'window_index']`
- event null counts after merge: `{'evt_active_fraction': 0, 'evt_burst_duration_median_s': 0, 'evt_interburst_gap_median_s': 0}`

Selector per-subject candidate rows after percentile-band filter:
- `{'brux1': {'label': 'bruxism', 'candidate_rows_after_match_filter': 25, 'candidate_start_s': {'count': 25, 'min': 2510.0, 'median': 8240.0, 'mean': 7412.0, 'max': 12140.0}, 'selected_start_s': {'count': 10, 'min': 2510.0, 'median': 8240.0, 'mean': 7442.0, 'max': 12140.0}, 'selected_start_s_values': [2510.0, 3260.0, 4280.0, 5870.0, 8210.0, 8270.0, 8570.0, 9680.0, 11630.0, 12140.0], 'candidate_relative_time_quantile': {'count': 25, 'min': 0.1, 'median': 0.5, 'mean': 0.5, 'max': 0.9}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.1, 'median': 0.5, 'mean': 0.5, 'max': 0.9}, 'selected_relative_time_quantile_values': [0.1, 0.2, 0.26666666666666666, 0.36666666666666664, 0.4666666666666667, 0.5333333333333333, 0.6333333333333333, 0.7333333333333333, 0.8, 0.9]}, 'brux2': {'label': 'bruxism', 'candidate_rows_after_match_filter': 89, 'candidate_start_s': {'count': 89, 'min': 4800.0, 'median': 14220.0, 'mean': 15309.438202247191, 'max': 24990.0}, 'selected_start_s': {'count': 10, 'min': 4800.0, 'median': 14580.0, 'mean': 15264.0, 'max': 24990.0}, 'selected_start_s_values': [4800.0, 7620.0, 12180.0, 13050.0, 14010.0, 15150.0, 18720.0, 19410.0, 22710.0, 24990.0], 'candidate_relative_time_quantile': {'count': 89, 'min': 0.1, 'median': 0.5, 'mean': 0.49999999999999994, 'max': 0.9}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.1, 'median': 0.5, 'mean': 0.5, 'max': 0.9}, 'selected_relative_time_quantile_values': [0.1, 0.19090909090909092, 0.2818181818181818, 0.36363636363636365, 0.45454545454545453, 0.5454545454545454, 0.6363636363636364, 0.7181818181818181, 0.8090909090909091, 0.9]}, 'n1': {'label': 'control', 'candidate_rows_after_match_filter': 44, 'candidate_start_s': {'count': 44, 'min': 7740.0, 'median': 24525.0, 'mean': 23421.81818181818, 'max': 33720.0}, 'selected_start_s': {'count': 10, 'min': 7740.0, 'median': 24360.0, 'mean': 23322.0, 'max': 33720.0}, 'selected_start_s_values': [7740.0, 11760.0, 19470.0, 22140.0, 24090.0, 24630.0, 27330.0, 30000.0, 32340.0, 33720.0], 'candidate_relative_time_quantile': {'count': 44, 'min': 0.10909090909090909, 'median': 0.5, 'mean': 0.5, 'max': 0.8909090909090909}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.10909090909090909, 'median': 0.5, 'mean': 0.5, 'max': 0.8909090909090909}, 'selected_relative_time_quantile_values': [0.10909090909090909, 0.2, 0.2909090909090909, 0.36363636363636365, 0.45454545454545453, 0.5454545454545454, 0.6363636363636364, 0.7090909090909091, 0.8, 0.8909090909090909]}, 'n2': {'label': 'control', 'candidate_rows_after_match_filter': 39, 'candidate_start_s': {'count': 39, 'min': 11880.0, 'median': 21060.0, 'mean': 22289.23076923077, 'max': 34200.0}, 'selected_start_s': {'count': 10, 'min': 11880.0, 'median': 21495.0, 'mean': 22698.0, 'max': 34200.0}, 'selected_start_s_values': [11880.0, 15120.0, 15780.0, 18240.0, 21000.0, 21990.0, 23430.0, 32490.0, 32850.0, 34200.0], 'candidate_relative_time_quantile': {'count': 39, 'min': 0.10416666666666667, 'median': 0.5, 'mean': 0.4999999999999999, 'max': 0.8958333333333334}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.10416666666666667, 'median': 0.5, 'mean': 0.4999999999999999, 'max': 0.8958333333333334}, 'selected_relative_time_quantile_values': [0.10416666666666667, 0.1875, 0.2708333333333333, 0.375, 0.4583333333333333, 0.5416666666666666, 0.625, 0.7291666666666666, 0.8125, 0.8958333333333334]}, 'n3': {'label': 'control', 'candidate_rows_after_match_filter': 60, 'candidate_start_s': {'count': 60, 'min': 11640.0, 'median': 25395.0, 'mean': 24092.5, 'max': 32040.0}, 'selected_start_s': {'count': 10, 'min': 11640.0, 'median': 25350.0, 'mean': 24033.0, 'max': 32040.0}, 'selected_start_s_values': [11640.0, 19920.0, 20730.0, 24660.0, 25050.0, 25650.0, 26010.0, 26820.0, 27810.0, 32040.0], 'candidate_relative_time_quantile': {'count': 60, 'min': 0.10666666666666667, 'median': 0.5, 'mean': 0.5, 'max': 0.8933333333333333}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.10666666666666667, 'median': 0.5, 'mean': 0.5, 'max': 0.8933333333333333}, 'selected_relative_time_quantile_values': [0.10666666666666667, 0.2, 0.28, 0.37333333333333335, 0.4533333333333333, 0.5466666666666666, 0.6266666666666667, 0.72, 0.8, 0.8933333333333333]}, 'n5': {'label': 'control', 'candidate_rows_after_match_filter': 30, 'candidate_start_s': {'count': 30, 'min': 5910.0, 'median': 14625.0, 'mean': 17101.0, 'max': 29670.0}, 'selected_start_s': {'count': 10, 'min': 5910.0, 'median': 14625.0, 'mean': 16830.0, 'max': 29670.0}, 'selected_start_s_values': [5910.0, 8190.0, 11970.0, 14100.0, 14580.0, 14670.0, 22590.0, 22890.0, 23730.0, 29670.0], 'candidate_relative_time_quantile': {'count': 30, 'min': 0.10810810810810811, 'median': 0.5, 'mean': 0.5, 'max': 0.8918918918918919}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.10810810810810811, 'median': 0.5, 'mean': 0.5, 'max': 0.8918918918918919}, 'selected_relative_time_quantile_values': [0.10810810810810811, 0.1891891891891892, 0.2702702702702703, 0.3783783783783784, 0.4594594594594595, 0.5405405405405406, 0.6216216216216216, 0.7297297297297297, 0.8108108108108109, 0.8918918918918919]}, 'n11': {'label': 'control', 'candidate_rows_after_match_filter': 32, 'candidate_start_s': {'count': 32, 'min': 2160.0, 'median': 14130.0, 'mean': 13685.625, 'max': 27690.0}, 'selected_start_s': {'count': 10, 'min': 2160.0, 'median': 14535.0, 'mean': 13755.0, 'max': 27690.0}, 'selected_start_s_values': [2160.0, 6870.0, 10380.0, 10920.0, 13020.0, 16050.0, 16380.0, 16920.0, 17160.0, 27690.0], 'candidate_relative_time_quantile': {'count': 32, 'min': 0.12195121951219512, 'median': 0.5, 'mean': 0.5, 'max': 0.8780487804878049}, 'selected_relative_time_quantile': {'count': 10, 'min': 0.12195121951219512, 'median': 0.5, 'mean': 0.5, 'max': 0.8780487804878049}, 'selected_relative_time_quantile_values': [0.12195121951219512, 0.1951219512195122, 0.2926829268292683, 0.36585365853658536, 0.4634146341463415, 0.5365853658536586, 0.6341463414634146, 0.7073170731707317, 0.8048780487804879, 0.8780487804878049]}}`

## Subject-level result vs pass45 and pass46 anchors
- balanced accuracy: pass45 `0.750` | pass46 `0.750` | pass47 `0.750`
- sensitivity: pass45 `0.500` | pass46 `0.500` | pass47 `0.500`
- specificity: pass45 `1.000` | pass46 `1.000` | pass47 `1.000`
- best-bruxism-minus-highest-control margin: pass45 `+0.295` | pass46 `+0.292` | pass47 `+0.335`
- highest control: pass45 `n11` `0.345` | pass46 `n5` `0.347` | pass47 `n5` `0.334`
- best bruxism subject: pass47 `brux1` `0.669`
- `brux2 - highest_control`: pass45 `-0.167` | pass46 `-0.151` | pass47 `-0.123`
- exact sensitivity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}`
- exact specificity CI: `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 5, 'trials': 5, 'low': 0.4781762498950185, 'high': 1.0}`
- subject Brier: `0.140`

Pass47 subject rows:
- `brux1` (bruxism): score `0.669` | predicted `bruxism` | positive-window fraction `0.700` | windows `10`
- `brux2` (bruxism): score `0.212` | predicted `control` | positive-window fraction `0.000` | windows `10`
- `n1` (control): score `0.196` | predicted `control` | positive-window fraction `0.000` | windows `10`
- `n2` (control): score `0.120` | predicted `control` | positive-window fraction `0.000` | windows `10`
- `n3` (control): score `0.081` | predicted `control` | positive-window fraction `0.000` | windows `10`
- `n5` (control): score `0.334` | predicted `control` | positive-window fraction `0.300` | windows `10`
- `n11` (control): score `0.283` | predicted `control` | positive-window fraction `0.200` | windows `10`

## New controls verdict
- `n1`: score `0.196` | predicted `control` | below threshold `True`
- `n2`: score `0.120` | predicted `control` | below threshold `True`
- all controls below threshold: `True`

## Shared-subject deltas vs the two 5-subject anchors
Against pass45:
- `brux1` (bruxism): pass47 `0.669` vs pass45 `0.641` | delta `+0.028` | labels pass47 `bruxism` / pass45 `bruxism`
- `brux2` (bruxism): pass47 `0.212` vs pass45 `0.178` | delta `+0.034` | labels pass47 `control` / pass45 `control`
- `n3` (control): pass47 `0.081` vs pass45 `0.134` | delta `-0.053` | labels pass47 `control` / pass45 `control`
- `n5` (control): pass47 `0.334` vs pass45 `0.337` | delta `-0.003` | labels pass47 `control` / pass45 `control`
- `n11` (control): pass47 `0.283` vs pass45 `0.345` | delta `-0.062` | labels pass47 `control` / pass45 `control`

Against pass46:
- `brux1` (bruxism): pass47 `0.669` vs pass46 `0.639` | delta `+0.030` | labels pass47 `bruxism` / pass46 `bruxism`
- `brux2` (bruxism): pass47 `0.212` vs pass46 `0.196` | delta `+0.016` | labels pass47 `control` / pass46 `control`
- `n3` (control): pass47 `0.081` vs pass46 `0.131` | delta `-0.050` | labels pass47 `control` / pass46 `control`
- `n5` (control): pass47 `0.334` vs pass46 `0.347` | delta `-0.013` | labels pass47 `control` / pass46 `control`
- `n11` (control): pass47 `0.283` vs pass46 `0.345` | delta `-0.062` | labels pass47 `control` / pass46 `control`

## Verdict
The first 7-subject control-expanded rerun preserves the repaired-A3 specificity story tightly enough to keep this branch alive: both new controls stay below threshold, all five controls remain predicted control, and the best-bruxism-minus-highest-control margin stays +0.335 even after adding `n1` and `n2`.

## A1-only replication note
A matched `A1-only` replication now looks justified as the next exact task because the first control-side stress test did not immediately collapse the repaired-A3 read; keep the same 7-subject subject set and frozen no-shape contract, and ask whether the control-expanded result is channel/stage-family specific or transfers honestly to the repaired `A1-only` scaffold.
