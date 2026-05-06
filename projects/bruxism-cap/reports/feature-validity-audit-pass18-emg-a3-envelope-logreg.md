# Pass 18 follow-up — EMG feature-validity audit on matched `EMG1-EMG2` `SLEEP-S2 + MCAP-A3-only` with envelope / burst features

Date: 2026-05-04
Status: follow-up validity audit completed for the pass18 replacement-family rerun; the main failure signal is still which handcrafted features lift controls above `brux1` on the saved matched scaffold

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
- `n5` (`control`): mean LOSO score `0.267`
- `n3` (`control`): mean LOSO score `0.245`
- `brux1` (`bruxism`): mean LOSO score `0.158`
- `n11` (`control`): mean LOSO score `0.104`
- `brux2` (`bruxism`): mean LOSO score `0.092`

This reproduces the pass15 ranking problem: `n3` and `n5` still sit above `brux1`, while `brux2` remains much lower.

## Repeated feature pattern among the high-score controls
- `min` appears in top-positive contributors for `2` high-score controls
- `sample_entropy` appears in top-positive contributors for `2` high-score controls
- `line_length` appears in top-positive contributors for `1` high-score controls
- `burst_fraction` appears in top-positive contributors for `1` high-score controls
- `ratio_alpha_delta` appears in top-positive contributors for `1` high-score controls
- `envelope_cv` appears in top-positive contributors for `1` high-score controls
- `rel_bp_alpha` appears in top-positive contributors for `1` high-score controls
- `zero_crossing_rate` appears in top-positive contributors for `1` high-score controls

## Per-subject contribution summaries

### `n5` (control)
- mean LOSO score: `0.267`
- mean logit: `-1.331`
- strongest positive contributors:
  - `sample_entropy` +0.089
  - `envelope_cv` +0.084
  - `rel_bp_alpha` +0.056
  - `min` +0.043
  - `zero_crossing_rate` +0.030
- strongest negative contributors:
  - `burst_rate_hz` -0.313
  - `line_length` -0.221
  - `ratio_alpha_beta` -0.137
  - `rel_bp_delta` -0.120
  - `bp_delta` -0.116

### `n3` (control)
- mean LOSO score: `0.245`
- mean logit: `-1.460`
- strongest positive contributors:
  - `line_length` +0.472
  - `burst_fraction` +0.333
  - `ratio_alpha_delta` +0.290
  - `min` +0.138
  - `sample_entropy` +0.126
- strongest negative contributors:
  - `burst_rate_hz` -0.914
  - `zero_crossing_rate` -0.314
  - `ratio_alpha_beta` -0.213
  - `rel_bp_delta` -0.184
  - `envelope_std` -0.164

### `brux1` (bruxism)
- mean LOSO score: `0.158`
- mean logit: `-931.199`
- strongest positive contributors:
  - `rel_bp_delta` +0.777
  - `burst_rate_hz` +0.670
  - `rel_bp_beta` +0.183
  - `rel_bp_alpha` +0.160
  - `envelope_cv` +0.112
- strongest negative contributors:
  - `mean` -817.817
  - `bp_theta` -65.207
  - `bp_alpha` -27.898
  - `ratio_theta_beta` -6.648
  - `zero_crossing_rate` -3.591

### `n11` (control)
- mean LOSO score: `0.104`
- mean logit: `-2.429`
- strongest positive contributors:
  - `burst_rate_hz` +0.084
  - `envelope_cv` +0.063
  - `p95_abs` +0.016
  - `rel_bp_theta` +0.015
  - `max` +0.011
- strongest negative contributors:
  - `line_length` -1.327
  - `ratio_alpha_beta` -0.231
  - `rel_bp_alpha` -0.144
  - `ratio_theta_beta` -0.122
  - `rel_bp_delta` -0.120

### `brux2` (bruxism)
- mean LOSO score: `0.092`
- mean logit: `-2.398`
- strongest positive contributors:
  - `line_length` +0.496
  - `min` +0.188
  - `ptp` +0.100
  - `sample_entropy` +0.052
  - `rel_bp_theta` +0.044
- strongest negative contributors:
  - `zero_crossing_rate` -1.361
  - `ratio_alpha_beta` -0.188
  - `rel_bp_beta` -0.114
  - `rel_bp_delta` -0.113
  - `envelope_std` -0.099

## Why `n3` and `n5` outrank `brux1`

### `n5` minus `brux1` (score gap `+0.109`)
- features increasing the gap toward `n5`:
  - `mean` +817.728
  - `bp_theta` +65.092
  - `bp_alpha` +27.807
  - `ratio_theta_beta` +6.532
  - `zero_crossing_rate` +3.621
  - `bp_delta` +3.008
- features pulling back toward `brux1`:
  - `burst_rate_hz` -0.983
  - `rel_bp_delta` -0.897
  - `line_length` -0.305
  - `rel_bp_beta` -0.288
  - `envelope_std` -0.185
  - `rel_bp_alpha` -0.104

### `n3` minus `brux1` (score gap `+0.087`)
- features increasing the gap toward `n3`:
  - `mean` +817.711
  - `bp_theta` +65.068
  - `bp_alpha` +27.787
  - `ratio_theta_beta` +6.499
  - `zero_crossing_rate` +3.276
  - `bp_delta` +2.988
- features pulling back toward `brux1`:
  - `burst_rate_hz` -1.584
  - `rel_bp_delta` -0.961
  - `rel_bp_beta` -0.287
  - `envelope_std` -0.260
  - `rel_bp_alpha` -0.187
  - `envelope_cv` -0.134

### `n11` minus `brux1` (score gap `-0.054`)
- features increasing the gap toward `n11`:
  - `mean` +817.731
  - `bp_theta` +65.089
  - `bp_alpha` +27.813
  - `ratio_theta_beta` +6.526
  - `zero_crossing_rate` +3.568
  - `bp_delta` +3.012
- features pulling back toward `brux1`:
  - `line_length` -1.410
  - `rel_bp_delta` -0.897
  - `burst_rate_hz` -0.586
  - `rel_bp_alpha` -0.304
  - `rel_bp_beta` -0.293
  - `envelope_std` -0.167

### `brux2` minus `brux1` (score gap `-0.067`)
- features increasing the gap toward `brux2`:
  - `mean` +817.747
  - `bp_theta` +65.112
  - `bp_alpha` +27.824
  - `ratio_theta_beta` +6.555
  - `bp_delta` +3.035
  - `bp_beta` +2.437
- features pulling back toward `brux1`:
  - `rel_bp_delta` -0.890
  - `burst_rate_hz` -0.660
  - `rel_bp_beta` -0.296
  - `rel_bp_alpha` -0.229
  - `envelope_std` -0.195
  - `envelope_cv` -0.189

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
