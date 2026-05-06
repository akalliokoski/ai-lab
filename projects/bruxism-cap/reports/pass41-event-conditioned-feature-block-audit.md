# Pass 41 — bounded event-conditioned EMG feature block audit on the repaired CAP scaffold

Date: 2026-05-05
Status: bounded representation audit completed. This pass keeps the repaired five-subject `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` percentile-band scaffold, the pass34 record-relative transform, the pass35 compact shape merge, the same train-time exclusions, and the same `logreg` LOSO contract fixed, then appends exactly 7 raw event-conditioned jaw-EMG features to ask one new question outside the closed pass37-pass40 floor family.

## Exact bounded feature logic implemented

Container held fixed:
- 30 s windows from the existing pass28 repaired selected table.
- No selector rerun, no channel pivot, no dataset switch, no model-family change.

Event rule:
- rectified basis: `abs(window_signal - mean(window_signal))`
- per-record threshold reference: `median_rectified` and `mad_rectified` computed from the full selected record channel before window slicing
- active sample threshold: `max(2.0 * median_rectified, median_rectified + 2.0 * mad_rectified, 1e-6)`
- burst = contiguous active run lasting `>= 0.25s`
- merge micro-gaps shorter than `0.08s`
- episode = one or more bursts with inter-burst gap `< 3.0s`
- phasic-like episode = `>=3` bursts and every burst duration in `[0.25, 2.0]s`

Appended event block:
- `evt_burst_count_30s, evt_episode_count_30s, evt_bursts_per_episode_mean, evt_active_fraction, evt_burst_duration_median_s, evt_interburst_gap_median_s, evt_phasic_like_episode_fraction`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
- Feature helper update: `projects/bruxism-cap/src/features.py`
- Pass41 feature table: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json`
- Summary JSON: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md`

## Scaffold parity checks
- pass36 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass40 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass41 counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- row-alignment warnings: `[]`
- unchanged train-time exclusions: `['bp_delta', 'rel_bp_delta', 'bp_theta', 'rel_bp_theta', 'bp_alpha', 'rel_bp_alpha', 'bp_beta', 'rel_bp_beta', 'ratio_theta_beta', 'ratio_alpha_beta', 'ratio_alpha_delta']`

## Apples-to-apples subject-level comparison against pass36 and pass40
- pass36 balanced accuracy: `0.750`
- pass40 balanced accuracy: `0.750`
- pass41 balanced accuracy: `0.583`
- pass36 sensitivity: `0.500`
- pass40 sensitivity: `0.500`
- pass41 sensitivity: `0.500`
- pass36 specificity: `1.000`
- pass40 specificity: `1.000`
- pass41 specificity: `0.667`
- pass36 best-bruxism-minus-highest-control margin: `+0.319`
- pass40 best-bruxism-minus-highest-control margin: `+0.363`
- pass41 best-bruxism-minus-highest-control margin: `+0.257`

Subject score deltas:
- `brux1`: pass36 `0.112` -> pass40 `0.112` -> pass41 `0.118` | delta vs pass36 `+0.006` | delta vs pass40 `+0.006` | predicted `control` -> `control`
- `brux2`: pass36 `0.808` -> pass40 `0.836` -> pass41 `0.803` | delta vs pass36 `-0.005` | delta vs pass40 `-0.033` | predicted `bruxism` -> `bruxism`
- `n3`: pass36 `0.068` -> pass40 `0.106` -> pass41 `0.154` | delta vs pass36 `+0.086` | delta vs pass40 `+0.047` | predicted `control` -> `control`
- `n5`: pass36 `0.385` -> pass40 `0.373` -> pass41 `0.200` | delta vs pass36 `-0.185` | delta vs pass40 `-0.173` | predicted `control` -> `control`
- `n11`: pass36 `0.489` -> pass40 `0.472` -> pass41 `0.546` | delta vs pass36 `+0.058` | delta vs pass40 `+0.074` | predicted `control` -> `bruxism`

## Did `brux1` improve without reopening controls?
- `brux1`: pass36 `0.112` -> pass40 `0.112` -> pass41 `0.118`
- `n3`: pass36 `0.068` -> pass40 `0.106` -> pass41 `0.154`
- `n5`: pass36 `0.385` -> pass40 `0.373` -> pass41 `0.200`
- `n11`: pass36 `0.489` -> pass40 `0.472` -> pass41 `0.546`
- pass41 `brux1 - n3`: `-0.036`
- pass41 `n5 - brux1`: `+0.083`
- pass41 `n11 - brux1`: `+0.429`

## What happened to the early `brux1` trio?
- early ranks `1-3` mean score: pass36 `2.14e-82` -> pass40 `9.10e-73` -> pass41 `1.76e-65`
- early ranks `1-3` event contribution mean on pass41: `+0.323`
- early ranks `1-3` amp/disp mean on pass41: `-161.205`
- early ranks `1-3` shape mean on pass41: `+0.254`

Early-window detail:
- rank `1` | window `3` | start `3500s` | score pass36 `1.63e-97` -> pass40 `1.15e-86` -> pass41 `8.36e-77` | event block pass41 `+0.661` | amp/disp pass41 `-178.583` | shape pass41 `+0.439` | other pass41 `+3.987`
- rank `2` | window `5` | start `3560s` | score pass36 `4.56e-84` -> pass40 `1.30e-74` -> pass41 `1.55e-66` | event block pass41 `-0.395` | amp/disp pass41 `-153.660` | shape pass41 `+0.163` | other pass41 `+4.036`
- rank `3` | window `7` | start `4370s` | score pass36 `6.37e-82` -> pass40 `2.72e-72` -> pass41 `5.13e-65` | event block pass41 `+0.704` | amp/disp pass41 `-151.372` | shape pass41 `+0.161` | other pass41 `+4.154`

## Event-block deltas against `brux1`
### `n5 - brux1`
- block sums: amp/disp `+47.497` | shape `-0.014` | event `-1.281` | other `-1.080`
- positive event deltas:
- `evt_episode_count_30s` contribution delta `+0.141` | z-mean delta `+0.023` | raw-mean delta `+0.000000`
- `evt_interburst_gap_median_s` contribution delta `+0.093` | z-mean delta `-0.138` | raw-mean delta `-0.139355`
- `evt_burst_count_30s` contribution delta `+0.026` | z-mean delta `+0.107` | raw-mean delta `+1.000000`
- `evt_bursts_per_episode_mean` contribution delta `+0.017` | z-mean delta `+0.144` | raw-mean delta `+1.333333`
- negative event deltas:
- `evt_burst_duration_median_s` contribution delta `-0.945` | z-mean delta `+1.717` | raw-mean delta `+10.051563`
- `evt_active_fraction` contribution delta `-0.567` | z-mean delta `+1.285` | raw-mean delta `+0.411406`
- `evt_phasic_like_episode_fraction` contribution delta `-0.046` | z-mean delta `+0.210` | raw-mean delta `+0.066667`

### `n11 - brux1`
- block sums: amp/disp `+47.774` | shape `+0.451` | event `+0.147` | other `-1.219`
- positive event deltas:
- `evt_episode_count_30s` contribution delta `+0.185` | z-mean delta `+0.266` | raw-mean delta `+0.200000`
- `evt_phasic_like_episode_fraction` contribution delta `+0.144` | z-mean delta `-0.391` | raw-mean delta `-0.133333`
- `evt_burst_duration_median_s` contribution delta `+0.100` | z-mean delta `+0.152` | raw-mean delta `+1.169531`
- `evt_interburst_gap_median_s` contribution delta `+0.053` | z-mean delta `-0.877` | raw-mean delta `-0.898535`
- `evt_burst_count_30s` contribution delta `+0.045` | z-mean delta `-0.146` | raw-mean delta `-1.500000`
- `evt_bursts_per_episode_mean` contribution delta `+0.040` | z-mean delta `-0.150` | raw-mean delta `-1.566667`
- negative event deltas:
- `evt_active_fraction` contribution delta `-0.420` | z-mean delta `+0.967` | raw-mean delta `+0.306042`

## Verdict
Pass41 raises `brux1`, but the gain comes with weaker control protection, so the event block is informative but not yet a clean benchmark improvement.

## Safest next bounded step
Keep the pass41 event block fixed and do one bounded ablation on the same table: test `pass36 + only the 3 least control-damaging event features` to isolate whether one count/duration component is causing the control reopening.
