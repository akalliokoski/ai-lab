# Pass 42 — same-table event-subset ablation on the pass41 table

Date: 2026-05-05
Status: bounded same-table ablation completed. This pass reuses the already-generated pass41 feature table, keeps the repaired five-subject `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` percentile-band scaffold and `logreg` LOSO contract fixed, and tests exactly one chosen 3-feature event subset instead of the full 7-feature pass41 block.

## Exact subset used
- `evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s`

## Exact implementation path
- input table reused directly: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- no selector rerun, no new feature invention, no channel pivot, no benchmark-contract change
- subset selection rule: maximize brux1 uplift among subsets that keep n11 < 0.5, then best-bruxism-minus-highest-control margin, then balanced accuracy
- subset-selection diagnostic sweep size: `35` choose-3 combinations from the existing 7 pass41 event features
- train-time feature removal for this pass: drop the four pass41 event features not in the chosen subset via `train_baseline.py --exclude-features-regex`, while keeping the pass36 backbone and base exclusion list unchanged

Top same-table subset candidates:
- `evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s` | bal acc `0.750` | specificity `1.000` | brux1 `0.136` | n11 `0.486` | margin `+0.339`
- `evt_bursts_per_episode_mean, evt_active_fraction, evt_phasic_like_episode_fraction` | bal acc `0.750` | specificity `1.000` | brux1 `0.134` | n11 `0.456` | margin `+0.347`
- `evt_burst_count_30s, evt_active_fraction, evt_phasic_like_episode_fraction` | bal acc `0.750` | specificity `1.000` | brux1 `0.129` | n11 `0.456` | margin `+0.344`
- `evt_episode_count_30s, evt_active_fraction, evt_burst_duration_median_s` | bal acc `0.750` | specificity `1.000` | brux1 `0.129` | n11 `0.494` | margin `+0.324`
- `evt_burst_count_30s, evt_bursts_per_episode_mean, evt_active_fraction` | bal acc `0.750` | specificity `1.000` | brux1 `0.123` | n11 `0.441` | margin `+0.346`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass42_same_table_event_subset_ablation.py`
- Reused pass41 feature table: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- Pass42 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json`
- Pass42 summary JSON: `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.json`
- Pass42 summary report: `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md`

## Scaffold parity checks
- pass36 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass40 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass41 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass42 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- row-alignment warnings: `[]`
- unchanged base train-time exclusions: `['^bp_', '^rel_bp_', '^ratio_']`
- additional pass42 dropped event features: `['evt_burst_count_30s', 'evt_episode_count_30s', 'evt_bursts_per_episode_mean', 'evt_phasic_like_episode_fraction']`

## Apples-to-apples subject-level comparison against pass36, pass40, and pass41
- pass36 balanced accuracy: `0.750`
- pass40 balanced accuracy: `0.750`
- pass41 balanced accuracy: `0.583`
- pass42 balanced accuracy: `0.750`
- pass36 sensitivity: `0.500`
- pass40 sensitivity: `0.500`
- pass41 sensitivity: `0.500`
- pass42 sensitivity: `0.500`
- pass36 specificity: `1.000`
- pass40 specificity: `1.000`
- pass41 specificity: `0.667`
- pass42 specificity: `1.000`
- pass36 best-bruxism-minus-highest-control margin: `+0.319`
- pass40 best-bruxism-minus-highest-control margin: `+0.363`
- pass41 best-bruxism-minus-highest-control margin: `+0.257`
- pass42 best-bruxism-minus-highest-control margin: `+0.339`

Subject score deltas:
- `brux1`: pass36 `0.112` -> pass40 `0.112` -> pass41 `0.118` -> pass42 `0.136` | delta vs pass36 `+0.025` | delta vs pass40 `+0.025` | delta vs pass41 `+0.019` | predicted pass36 `control` -> pass41 `control` -> pass42 `control`
- `brux2`: pass36 `0.808` -> pass40 `0.836` -> pass41 `0.803` -> pass42 `0.825` | delta vs pass36 `+0.017` | delta vs pass40 `-0.011` | delta vs pass41 `+0.022` | predicted pass36 `bruxism` -> pass41 `bruxism` -> pass42 `bruxism`
- `n3`: pass36 `0.068` -> pass40 `0.106` -> pass41 `0.154` -> pass42 `0.155` | delta vs pass36 `+0.087` | delta vs pass40 `+0.049` | delta vs pass41 `+0.001` | predicted pass36 `control` -> pass41 `control` -> pass42 `control`
- `n5`: pass36 `0.385` -> pass40 `0.373` -> pass41 `0.200` -> pass42 `0.199` | delta vs pass36 `-0.186` | delta vs pass40 `-0.173` | delta vs pass41 `-0.001` | predicted pass36 `control` -> pass41 `control` -> pass42 `control`
- `n11`: pass36 `0.489` -> pass40 `0.472` -> pass41 `0.546` -> pass42 `0.486` | delta vs pass36 `-0.002` | delta vs pass40 `+0.014` | delta vs pass41 `-0.060` | predicted pass36 `control` -> pass41 `bruxism` -> pass42 `control`

## Did the brux1 lift survive while n11 fell back below threshold?
- `brux1`: pass36 `0.112` -> pass41 `0.118` -> pass42 `0.136`
- `n11`: pass36 `0.489` -> pass41 `0.546` -> pass42 `0.486`
- `n5`: pass36 `0.385` -> pass41 `0.200` -> pass42 `0.199`
- `n3`: pass36 `0.068` -> pass41 `0.154` -> pass42 `0.155`
- pass42 `brux1 - n3`: `-0.019`
- pass42 `n5 - brux1`: `+0.063`
- pass42 `n11 - brux1`: `+0.350`
- verdict: Yes: the chosen subset keeps the pass41 brux1 lift directionally alive while moving n11 back below threshold and restoring the pass36/pass40 subject-level surface.

## Event-feature deltas against brux1 for the chosen subset pass
### `n5 - brux1`
- block sums: amp/disp `+48.629` | shape `-0.206` | event `-1.529` | other `-1.411`
- positive event deltas:
- `evt_interburst_gap_median_s` contribution delta `+0.081` | z-mean delta `-0.138` | raw-mean delta `-0.139355`
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.995` | z-mean delta `+1.717` | raw-mean delta `+10.051563`
- `evt_active_fraction` contribution delta `-0.615` | z-mean delta `+1.285` | raw-mean delta `+0.411406`

### `n11 - brux1`
- block sums: amp/disp `+48.902` | shape `+0.318` | event `-0.469` | other `-1.520`
- positive event deltas:
- `evt_burst_duration_median_s` contribution delta `+0.081` | z-mean delta `+0.152` | raw-mean delta `+1.169531`
- negative event deltas:
- `evt_active_fraction` contribution delta `-0.470` | z-mean delta `+0.967` | raw-mean delta `+0.306042`
- `evt_interburst_gap_median_s` contribution delta `-0.080` | z-mean delta `-0.877` | raw-mean delta `-0.898535`

## Safest next bounded step
Keep the same pass42 subset fixed and compare the exact same subset on matched A1-only vs A3-only EMG tables before changing model family.
