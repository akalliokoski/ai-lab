# Pass 16 — EMG feature-validity audit on matched `EMG1-EMG2` `SLEEP-S2 + MCAP-A3-only`

Date: 2026-05-04
Status: bounded EMG-first validity audit completed; the main failure signal is now better localized to which handcrafted features lift controls above `brux1` on the saved pass14 scaffold

## Why this audit exists

Pass15 showed that threshold tuning is a dead end for the current matched EMG run: `n3` and `n5` still outrank `brux1`, so no threshold rescues subject sensitivity without false positives.

This pass makes exactly one bounded increment:
- keep the same pass14 matched `EMG1-EMG2` `A3-only` dataset fixed
- keep the same model family fixed (`logreg`)
- rebuild the LOSO folds and inspect per-subject feature contributions to explain why controls outrank `brux1`

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_feature_validity.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`
- Primary features CSV: `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- Primary LOSO report context: `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`

## Key score ordering reproduced
- `n3` (`control`): mean LOSO score `0.267`
- `n5` (`control`): mean LOSO score `0.266`
- `brux1` (`bruxism`): mean LOSO score `0.176`
- `n11` (`control`): mean LOSO score `0.095`
- `brux2` (`bruxism`): mean LOSO score `0.074`

This reproduces the pass15 ranking problem: `n3` and `n5` still sit above `brux1`, while `brux2` remains much lower.

## Repeated feature pattern among the high-score controls
- `ratio_alpha_delta` appears in top-positive contributors for `2` high-score controls
- `min` appears in top-positive contributors for `2` high-score controls
- `sample_entropy` appears in top-positive contributors for `2` high-score controls
- `line_length` appears in top-positive contributors for `1` high-score controls
- `rel_bp_theta` appears in top-positive contributors for `1` high-score controls
- `rel_bp_alpha` appears in top-positive contributors for `1` high-score controls
- `zero_crossing_rate` appears in top-positive contributors for `1` high-score controls

## Per-subject contribution summaries

### `n3` (control)
- mean LOSO score: `0.267`
- mean logit: `-1.355`
- strongest positive contributors:
  - `line_length` +0.463
  - `ratio_alpha_delta` +0.231
  - `rel_bp_theta` +0.049
  - `min` +0.033
  - `sample_entropy` -0.017
- strongest negative contributors:
  - `zero_crossing_rate` -0.349
  - `ratio_alpha_beta` -0.243
  - `rel_bp_delta` -0.227
  - `std` -0.202
  - `rms` -0.201

### `n5` (control)
- mean LOSO score: `0.266`
- mean logit: `-1.270`
- strongest positive contributors:
  - `rel_bp_alpha` +0.058
  - `sample_entropy` +0.038
  - `ratio_alpha_delta` +0.036
  - `zero_crossing_rate` +0.033
  - `min` +0.012
- strongest negative contributors:
  - `line_length` -0.207
  - `ratio_alpha_beta` -0.160
  - `rel_bp_delta` -0.142
  - `ratio_theta_beta` -0.141
  - `bp_delta` -0.139

### `brux1` (bruxism)
- mean LOSO score: `0.176`
- mean logit: `-981.393`
- strongest positive contributors:
  - `rel_bp_delta` +1.058
  - `rel_bp_beta` +0.366
  - `ratio_alpha_beta` +0.251
  - `rel_bp_alpha` +0.240
  - `line_length` +0.109
- strongest negative contributors:
  - `mean` -853.624
  - `bp_theta` -76.231
  - `bp_alpha` -31.114
  - `ratio_theta_beta` -7.067
  - `bp_delta` -4.379

### `n11` (control)
- mean LOSO score: `0.095`
- mean logit: `-2.540`
- strongest positive contributors:
  - `sample_entropy` +0.022
  - `min` +0.007
  - `rel_bp_theta` -0.004
  - `ratio_alpha_delta` -0.008
  - `ptp` -0.009
- strongest negative contributors:
  - `line_length` -1.232
  - `ratio_alpha_beta` -0.260
  - `rel_bp_delta` -0.158
  - `rel_bp_alpha` -0.152
  - `ratio_theta_beta` -0.151

### `brux2` (bruxism)
- mean LOSO score: `0.074`
- mean logit: `-2.627`
- strongest positive contributors:
  - `line_length` +0.460
  - `min` +0.123
  - `ptp` +0.043
  - `rel_bp_theta` +0.032
  - `ratio_alpha_delta` +0.001
- strongest negative contributors:
  - `zero_crossing_rate` -1.396
  - `ratio_alpha_beta` -0.195
  - `rel_bp_beta` -0.129
  - `rel_bp_delta` -0.127
  - `std` -0.113

## Why `n3` and `n5` outrank `brux1`

### `n3` minus `brux1` (score gap `+0.091`)
- features increasing the gap toward `n3`:
  - `mean` +853.499
  - `bp_theta` +76.071
  - `bp_alpha` +30.985
  - `ratio_theta_beta` +6.894
  - `bp_delta` +4.219
  - `zero_crossing_rate` +3.381
- features pulling back toward `brux1`:
  - `rel_bp_delta` -1.285
  - `rel_bp_beta` -0.521
  - `ratio_alpha_beta` -0.494
  - `rel_bp_alpha` -0.282
  - `sample_entropy` -0.085
  - `min` +0.094

### `n5` minus `brux1` (score gap `+0.090`)
- features increasing the gap toward `n5`:
  - `mean` +853.515
  - `bp_theta` +76.093
  - `bp_alpha` +31.007
  - `ratio_theta_beta` +6.926
  - `bp_delta` +4.241
  - `zero_crossing_rate` +3.763
- features pulling back toward `brux1`:
  - `rel_bp_delta` -1.200
  - `rel_bp_beta` -0.485
  - `ratio_alpha_beta` -0.410
  - `line_length` -0.316
  - `rel_bp_alpha` -0.182
  - `sample_entropy` -0.030

### `n11` minus `brux1` (score gap `-0.081`)
- features increasing the gap toward `n11`:
  - `mean` +853.514
  - `bp_theta` +76.086
  - `bp_alpha` +31.007
  - `ratio_theta_beta` +6.916
  - `bp_delta` +4.238
  - `zero_crossing_rate` +3.705
- features pulling back toward `brux1`:
  - `line_length` -1.341
  - `rel_bp_delta` -1.216
  - `rel_bp_beta` -0.516
  - `ratio_alpha_beta` -0.511
  - `rel_bp_alpha` -0.392
  - `sample_entropy` -0.047

### `brux2` minus `brux1` (score gap `-0.102`)
- features increasing the gap toward `brux2`:
  - `mean` +853.548
  - `bp_theta` +76.128
  - `bp_alpha` +31.035
  - `ratio_theta_beta` +6.966
  - `bp_delta` +4.282
  - `bp_beta` +2.937
- features pulling back toward `brux1`:
  - `rel_bp_delta` -1.185
  - `rel_bp_beta` -0.496
  - `ratio_alpha_beta` -0.446
  - `rel_bp_alpha` -0.312
  - `sample_entropy` -0.134
  - `ratio_alpha_delta` -0.017

## Interpretation

1. The current EMG feature set is still partly EEG-shaped: relative bandpower / ratio features remain large contributors even though the project is now EMG-first.
2. The controls that outrank `brux1` do so through a small recurring feature family rather than through threshold quirks alone.
3. `brux2` remains a different failure mode from `brux1`: its score is not merely slightly below the controls, it is substantially lower, so one patch aimed only at `brux1` may not rescue both bruxism subjects.
4. This is still a validity note, not a baseline win. The audit narrows the next patch target to one small EMG-aligned feature-family change rather than another threshold or model sweep.

## Best next bounded step

Keep the matched subset and model family fixed, then run one small feature patch only:
- either drop the EEG-style relative bandpower / ratio family from the EMG recipe for a matched rerun, or
- replace that family with one compact amplitude-burst-oriented EMG summary family.

The safer next experiment is the ablation first: remove the band-ratio family on the same pass14 scaffold and compare whether the subject ranking becomes less hostile to `brux1` without inflating control false positives.
