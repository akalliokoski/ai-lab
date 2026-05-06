# Pass 44 — repaired A3-only scaffold rebuild with the fixed pass42 event subset

Date: 2026-05-05
Status: bounded scaffold-rebuild test completed. This pass keeps the verified five-subject set, `EMG1-EMG2`, `logreg` LOSO, the pass42 event subset, and the base train-time exclusions fixed while rebuilding `A3-only` on the repaired percentile-band / time-aware scaffold instead of the old matched14 surface.

## Exact implementation path
- fixed pass42 subset carried over unchanged: `evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s`
- rebuilt the exclusive `SLEEP-S2 + MCAP-A3-only` full `EMG1-EMG2` pool from raw EDF windows with the current feature extractor so the repaired A3 branch includes the same compact shape descriptors used by the active pass36/pass41/pass42 backbone
- re-applied the repaired percentile-band selector in time-aware mode: `cap=10`, `lower_quantile=0.10`, `upper_quantile=0.90`
- applied the same pass34 within-record robust transform only to the retained record-relative feature family: `mean, max, ptp, line_length, zero_crossing_rate, rectified_std, envelope_std, envelope_cv, rectified_mean, envelope_mean, p95_abs`
- appended only the fixed three event features by row key merge: `['subject_id', 'start_s', 'end_s', 'window_index']`
- reran `train_baseline.py --cv loso` with unchanged base exclusions `['^bp_', '^rel_bp_', '^ratio_']` plus regex drops for the four pass41 event terms not kept in pass42/pass44

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass44_repaired_a3_event_subset_rebuild.py`
- Full rebuilt A3 feature pool: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_full_envelope_shape.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass44-emg-a3-pct10-90-shape.json`
- Intermediate repaired A3 selected table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_shape.csv`
- Final repaired A3 event-subset table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json`
- Summary JSON: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.json`
- Summary memo: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md`

## Scaffold checks: old A3 surface versus repaired A3 surface
- pass42 repaired A1 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass43 old-surface A3 counts by subject: `{'brux1': 14, 'brux2': 14, 'n11': 14, 'n3': 14, 'n5': 14}` | total rows `70`
- pass44 rebuilt full A3 counts by subject: `{'brux1': 31, 'brux2': 111, 'n3': 76, 'n5': 38, 'n11': 42}` | total rows `298`
- pass44 repaired selected A3 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- pass44 final repaired A3 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}` | total rows `50`
- selector mode: `percentile-band` with percentile band `{'lower_quantile': 0.1, 'upper_quantile': 0.9}`
- event null counts after repaired A3 merge: `{'evt_active_fraction': 0, 'evt_burst_duration_median_s': 0, 'evt_interburst_gap_median_s': 0}`
- pass44 channels: `['EMG1-EMG2']`

## Subject-level comparison: pass42 repaired A1 vs pass43 old-surface A3 vs pass44 repaired-surface A3
- balanced accuracy: pass42 `0.750` | pass43 `0.500` | pass44 `0.750`
- sensitivity: pass42 `0.500` | pass43 `0.000` | pass44 `0.500`
- specificity: pass42 `1.000` | pass43 `1.000` | pass44 `1.000`
- best-bruxism-minus-highest-control margin: pass42 `+0.339` | pass43 `-0.134` | pass44 `+0.138`
- highest control on pass44: `n11` at `0.395`
- pass44 `brux1 - n3`: `+0.499`

Subject score rows:
- `brux1`: pass42 repaired A1 `0.136` -> pass43 old-surface A3 `0.176` -> pass44 repaired-surface A3 `0.532` | delta pass44 vs pass42 `+0.396` | delta pass44 vs pass43 `+0.357` | predicted pass42 `control` -> pass43 `control` -> pass44 `bruxism`
- `brux2`: pass42 repaired A1 `0.825` -> pass43 old-surface A3 `0.130` -> pass44 repaired-surface A3 `0.123` | delta pass44 vs pass42 `-0.702` | delta pass44 vs pass43 `-0.007` | predicted pass42 `bruxism` -> pass43 `control` -> pass44 `control`
- `n3`: pass42 repaired A1 `0.155` -> pass43 old-surface A3 `0.208` -> pass44 repaired-surface A3 `0.034` | delta pass44 vs pass42 `-0.122` | delta pass44 vs pass43 `-0.174` | predicted pass42 `control` -> pass43 `control` -> pass44 `control`
- `n5`: pass42 repaired A1 `0.199` -> pass43 old-surface A3 `0.128` -> pass44 repaired-surface A3 `0.365` | delta pass44 vs pass42 `+0.166` | delta pass44 vs pass43 `+0.237` | predicted pass42 `control` -> pass43 `control` -> pass44 `control`
- `n11`: pass42 repaired A1 `0.486` -> pass43 old-surface A3 `0.310` -> pass44 repaired-surface A3 `0.395` | delta pass44 vs pass42 `-0.091` | delta pass44 vs pass43 `+0.085` | predicted pass42 `control` -> pass43 `control` -> pass44 `control`

## Fixed-subset contributor checks on the repaired A3 surface
### `n3 - brux1`
- block sums: amp/disp `-23.175` | shape `+0.007` | event `+1.290` | other `-2.879`
- positive event deltas:
- `evt_active_fraction` contribution delta `+0.848` | z-mean delta `-1.701` | raw-mean delta `-0.455599`
- `evt_burst_duration_median_s` contribution delta `+0.404` | z-mean delta `-0.424` | raw-mean delta `-4.323926`
- `evt_interburst_gap_median_s` contribution delta `+0.038` | z-mean delta `+1.231` | raw-mean delta `+1.301563`
- negative event deltas:
- none

### `n11 - brux1`
- block sums: amp/disp `-14.286` | shape `+0.847` | event `-0.637` | other `-1.487`
- positive event deltas:
- `evt_active_fraction` contribution delta `+0.062` | z-mean delta `+0.025` | raw-mean delta `+0.006615`
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.658` | z-mean delta `+1.056` | raw-mean delta `+9.787207`
- `evt_interburst_gap_median_s` contribution delta `-0.041` | z-mean delta `+1.038` | raw-mean delta `+1.098047`

## Verdict
scaffold mismatch was the main blocker.
