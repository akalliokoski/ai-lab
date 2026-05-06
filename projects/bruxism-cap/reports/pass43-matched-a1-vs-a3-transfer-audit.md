# Pass 43 — matched A1-vs-A3 transfer audit for the verified pass42 event subset

Date: 2026-05-05
Status: bounded transfer audit completed. This pass keeps the verified pass42 3-feature event subset fixed, reuses the repaired A1-only pass42 result as the source anchor, appends the same subset onto the closest existing matched A3-only EMG surface, and compares subject-level LOSO behavior without changing model family.

## Exact implementation path
- fixed pass42 subset carried over unchanged: `evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s`
- repaired A1 anchor reused directly from `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv` plus the saved pass42 LOSO report
- closest matched A3 surface started from `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- new work in this pass: recompute only the same three event features for each existing pass14 A3 row, merge them onto that saved matched14 table, then rerun `train_baseline.py --cv loso` with the same base regex exclusions and no broader feature changes
- unchanged base train-time exclusions: `['^bp_', '^rel_bp_', '^ratio_']`
- additional dropped pass41 event features not kept in this transfer audit: `['evt_burst_count_30s', 'evt_episode_count_30s', 'evt_bursts_per_episode_mean', 'evt_phasic_like_episode_fraction']`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass43_matched_a1_vs_a3_transfer_audit.py`
- New pass43 A3 feature table: `projects/bruxism-cap/data/window_features_pass43_emg_s2_mcap_a3_only_matched14_eventsubset.csv`
- New pass43 A3 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass43-emg-a3-matched14-eventsubset.json`
- Summary JSON: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md`

## Verified counts and parity checks
- repaired A1 pass42 counts by subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- matched A3 pass14 baseline counts by subject: `{'brux1': 14, 'brux2': 14, 'n3': 14, 'n5': 14, 'n11': 14}`
- matched A3 pass43 counts by subject: `{'brux1': 14, 'brux2': 14, 'n11': 14, 'n3': 14, 'n5': 14}`
- shared subjects: `['brux1', 'brux2', 'n11', 'n3', 'n5']`
- A1 channel(s): `['EMG1-EMG2']`
- A3 channel(s): `['EMG1-EMG2']`
- event merge keys: `['subject_id', 'start_s', 'end_s', 'window_index']`
- event null counts after A3 merge: `{'evt_active_fraction': 0, 'evt_burst_duration_median_s': 0, 'evt_interburst_gap_median_s': 0}`
- parity warnings: `['row counts differ across compared surfaces: repaired A1 rows=50 matched A3 rows=70']`

## Apples-to-apples subject-level comparison of the fixed subset
- pass14 A3 baseline balanced accuracy: `0.500`
- pass42 A1 fixed-subset balanced accuracy: `0.750`
- pass43 A3 fixed-subset balanced accuracy: `0.500`
- pass14 A3 baseline sensitivity: `0.000`
- pass42 A1 fixed-subset sensitivity: `0.500`
- pass43 A3 fixed-subset sensitivity: `0.000`
- pass14 A3 baseline specificity: `1.000`
- pass42 A1 fixed-subset specificity: `1.000`
- pass43 A3 fixed-subset specificity: `1.000`
- pass14 A3 baseline best-bruxism-minus-highest-control margin: `-0.091`
- pass42 A1 fixed-subset best-bruxism-minus-highest-control margin: `+0.339`
- pass43 A3 fixed-subset best-bruxism-minus-highest-control margin: `-0.134`

Subject score deltas:
- `brux1`: pass14 A3 `0.176` -> pass42 A1 `0.136` -> pass43 A3 `0.176` | delta pass43 vs pass14 `-0.001` | delta pass43 vs pass42 `+0.039` | predicted pass14 `control` -> pass42 `control` -> pass43 `control`
- `brux2`: pass14 A3 `0.074` -> pass42 A1 `0.825` -> pass43 A3 `0.130` | delta pass43 vs pass14 `+0.055` | delta pass43 vs pass42 `-0.695` | predicted pass14 `control` -> pass42 `bruxism` -> pass43 `control`
- `n3`: pass14 A3 `0.267` -> pass42 A1 `0.155` -> pass43 A3 `0.208` | delta pass43 vs pass14 `-0.059` | delta pass43 vs pass42 `+0.052` | predicted pass14 `control` -> pass42 `control` -> pass43 `control`
- `n5`: pass14 A3 `0.266` -> pass42 A1 `0.199` -> pass43 A3 `0.128` | delta pass43 vs pass14 `-0.138` | delta pass43 vs pass42 `-0.072` | predicted pass14 `control` -> pass42 `control` -> pass43 `control`
- `n11`: pass14 A3 `0.095` -> pass42 A1 `0.486` -> pass43 A3 `0.310` | delta pass43 vs pass14 `+0.214` | delta pass43 vs pass42 `-0.177` | predicted pass14 `control` -> pass42 `control` -> pass43 `control`

## Did brux1 improve, hold, or collapse on A3?
- `brux1`: pass14 A3 baseline `0.176` -> pass42 repaired A1 subset `0.136` -> pass43 A3 subset `0.176`
- `brux2`: pass14 A3 baseline `0.074` -> pass42 repaired A1 subset `0.825` -> pass43 A3 subset `0.130`
- highest A3 control after transfer: `n11` at `0.310`
- pass43 `brux1 - highest_control`: `-0.134`
- pass43 `brux1 - n3`: `-0.032`
- transfer status: `holds`
- overall honest transfer verdict: `collapses`
- verdict: The fixed pass42 event subset does not transfer honestly on the matched A3 surface: brux1 itself roughly holds, but subject-level sensitivity collapses back to zero and the overall A3 surface remains below the repaired A1 result.

## A3 control-side contributors against `brux1` on the fixed subset transfer run
### `n3 - brux1`
- block sums: amp/disp `+818.186` | shape `+0.000` | event `-0.867` | other `+3.733`
- positive event deltas:
- none
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.449` | z-mean delta `+1.273` | raw-mean delta `+12.506069`
- `evt_active_fraction` contribution delta `-0.262` | z-mean delta `+0.581` | raw-mean delta `+0.168001`
- `evt_interburst_gap_median_s` contribution delta `-0.156` | z-mean delta `+0.835` | raw-mean delta `+0.883371`

### `n5 - brux1`
- block sums: amp/disp `+817.899` | shape `+0.000` | event `-1.096` | other `+3.902`
- positive event deltas:
- none
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.692` | z-mean delta `+1.678` | raw-mean delta `+16.118094`
- `evt_active_fraction` contribution delta `-0.318` | z-mean delta `+0.558` | raw-mean delta `+0.154776`
- `evt_interburst_gap_median_s` contribution delta `-0.085` | z-mean delta `+1.383` | raw-mean delta `+1.411203`

### `n11 - brux1`
- block sums: amp/disp `+818.046` | shape `+0.000` | event `+0.113` | other `+3.613`
- positive event deltas:
- `evt_active_fraction` contribution delta `+0.182` | z-mean delta `-0.149` | raw-mean delta `-0.040830`
- `evt_interburst_gap_median_s` contribution delta `+0.033` | z-mean delta `+0.266` | raw-mean delta `+0.282785`
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.102` | z-mean delta `+0.518` | raw-mean delta `+5.366350`

## Safest next bounded step
Do not broaden the feature family. Keep the same 3-feature subset fixed and rebuild only the A3-only table on the repaired percentile-band/time-aware EMG scaffold to separate family-transfer failure from old-surface mismatch.
