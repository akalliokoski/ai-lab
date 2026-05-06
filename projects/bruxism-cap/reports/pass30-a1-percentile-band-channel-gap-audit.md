# Pass 30 — percentile-band `A1-only` cross-channel gap audit (`EMG1-EMG2` vs `C4-P4`)

Date: 2026-05-05
Status: bounded validity audit completed; on the same repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold, `brux1` still trails `n3` under both channels, but only `C4-P4` strongly flips `brux2` above `n3`, while `EMG1-EMG2` stays control-dominant because `mean` and crossing/amplitude terms remain hostile on the held-out `bruxism` folds

## Why this audit exists

Pass29 narrowed the remaining benchmark question sharply:
- the repaired percentile-band selector is usable and matched across channels
- `C4-P4` beats matched `EMG1-EMG2` on the honest LOSO surface without overturning the EMG-first project framing
- the remaining failure is now specific: `brux1` remains just below `n3` under both channels, while `brux2` recovers only under `C4-P4`

This pass makes exactly one bounded increment:
- keep the same verified `5`-subject exclusive `SLEEP-S2 + MCAP-A1-only` percentile-band scaffold fixed
- keep the same train-time exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the subject-score gaps directly instead of launching another extraction rewrite

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`
- EMG feature CSV: `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- C4 feature CSV: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- EMG context report: `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- C4 context report: `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`

## Matched-scaffold verification
- Selected rows are timing-matched across channels: `True`.
- Shared columns checked: `subject_id, window_index, start_s, end_s, relative_time_quantile, time_match_rank`.
- Every subject keeps the same `10` selected windows, so this audit compares channel behavior rather than hidden availability drift.

## Reproduced subject score surfaces

### `EMG1-EMG2` (`logreg`)
- `n3` (control): mean LOSO score `0.530` | positive-window fraction `0.800` | start_s mean `18618.0`
- `brux1` (bruxism): mean LOSO score `0.270` | positive-window fraction `0.000` | start_s mean `7733.0`
- `brux2` (bruxism): mean LOSO score `0.036` | positive-window fraction `0.000` | start_s mean `20577.0`

### `C4-P4` (`logreg`)
- `brux2` (bruxism): mean LOSO score `0.959` | positive-window fraction `1.000` | start_s mean `20577.0`
- `n3` (control): mean LOSO score `0.417` | positive-window fraction `0.400` | start_s mean `18618.0`
- `brux1` (bruxism): mean LOSO score `0.405` | positive-window fraction `0.300` | start_s mean `7733.0`

## Key score-gap findings
- EMG `n3 - brux1` gap: `+0.260`.
- C4 `n3 - brux1` gap: `+0.012`.
- EMG `brux2 - n3` gap: `-0.494`.
- C4 `brux2 - n3` gap: `+0.542`.

So the repaired scaffold still leaves one shared hard case (`brux1 < n3`) under both channels, but the channel-level separation is now mostly about `brux2`: `C4-P4` pushes it decisively above `n3`, whereas `EMG1-EMG2` still leaves it far below.

## Focused feature deltas

### `EMG1-EMG2`: why `n3` stays above `brux1`
- features pushing toward `n3`:
  - `mean` contribution delta `+156.609` | z-mean delta `-114.418` | raw-mean delta `-0.000001`
  - `max` contribution delta `+1.825` | z-mean delta `-15.420` | raw-mean delta `-0.000283`
  - `ptp` contribution delta `+1.414` | z-mean delta `-10.722` | raw-mean delta `-0.000389`
  - `zero_crossing_rate` contribution delta `+1.348` | z-mean delta `+0.975` | raw-mean delta `+0.060583`
  - `line_length` contribution delta `+1.138` | z-mean delta `-0.761` | raw-mean delta `-0.005808`
- features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-0.781` | z-mean delta `+1.264` | raw-mean delta `+10.683333`
  - `sample_entropy` contribution delta `-0.302` | z-mean delta `+3.257` | raw-mean delta `+0.515308`
  - `envelope_mean` contribution delta `-0.119` | z-mean delta `-3.394` | raw-mean delta `-0.000003`
  - `rectified_mean` contribution delta `-0.119` | z-mean delta `-3.391` | raw-mean delta `-0.000003`
  - `p95_abs` contribution delta `-0.052` | z-mean delta `-3.111` | raw-mean delta `-0.000008`

### `C4-P4`: why `n3` still barely stays above `brux1`
- features pushing toward `n3`:
  - `max` contribution delta `+4.287` | z-mean delta `-26.895` | raw-mean delta `-0.000273`
  - `mean` contribution delta `+1.339` | z-mean delta `-6.871` | raw-mean delta `-0.000001`
  - `envelope_cv` contribution delta `+0.562` | z-mean delta `-3.939` | raw-mean delta `-0.528116`
  - `zero_crossing_rate` contribution delta `+0.266` | z-mean delta `+0.033` | raw-mean delta `+0.000306`
  - `burst_rate_hz` contribution delta `+0.252` | z-mean delta `+1.109` | raw-mean delta `+0.803333`
- features pushing back toward `brux1`:
  - `line_length` contribution delta `-5.660` | z-mean delta `-11.425` | raw-mean delta `-0.005746`
  - `ptp` contribution delta `-4.200` | z-mean delta `-18.684` | raw-mean delta `-0.000374`
  - `min` contribution delta `-4.088` | z-mean delta `+8.299` | raw-mean delta `+0.000101`
  - `std` contribution delta `-0.393` | z-mean delta `-6.688` | raw-mean delta `-0.000011`
  - `envelope_mean` contribution delta `-0.201` | z-mean delta `-2.636` | raw-mean delta `-0.000003`

### `EMG1-EMG2`: why `brux2` fails to clear `n3`
- features pushing toward `brux2`:
  - `burst_rate_hz` contribution delta `+0.234` | z-mean delta `-1.118` | raw-mean delta `-11.286667`
  - `sample_entropy` contribution delta `+0.042` | z-mean delta `-0.169` | raw-mean delta `-0.069435`
  - `std` contribution delta `+0.037` | z-mean delta `+0.120` | raw-mean delta `+0.000001`
  - `max` contribution delta `+0.032` | z-mean delta `+0.031` | raw-mean delta `+0.000006`
  - `mean` contribution delta `+0.029` | z-mean delta `-0.029` | raw-mean delta `-0.000000`
- features pushing back toward `n3`:
  - `zero_crossing_rate` contribution delta `-2.417` | z-mean delta `+4.054` | raw-mean delta `+0.203114`
  - `line_length` contribution delta `-0.992` | z-mean delta `+0.711` | raw-mean delta `+0.005340`
  - `burst_fraction` contribution delta `-0.386` | z-mean delta `-0.475` | raw-mean delta `-0.014258`
  - `min` contribution delta `-0.008` | z-mean delta `-0.094` | raw-mean delta `-0.000007`
  - `envelope_cv` contribution delta `-0.007` | z-mean delta `+0.175` | raw-mean delta `+0.087651`

### `C4-P4`: why `brux2` clears `n3`
- features pushing toward `brux2`:
  - `zero_crossing_rate` contribution delta `+4.779` | z-mean delta `+7.692` | raw-mean delta `+0.025415`
  - `sample_entropy` contribution delta `+0.130` | z-mean delta `+0.076` | raw-mean delta `+0.027182`
  - `envelope_cv` contribution delta `+0.066` | z-mean delta `-0.170` | raw-mean delta `-0.064475`
  - `line_length` contribution delta `+0.041` | z-mean delta `+0.089` | raw-mean delta `+0.000353`
  - `min` contribution delta `+0.020` | z-mean delta `-0.099` | raw-mean delta `-0.000007`
- features pushing back toward `n3`:
  - `burst_rate_hz` contribution delta `-0.219` | z-mean delta `+0.649` | raw-mean delta `+0.513333`
  - `burst_fraction` contribution delta `-0.182` | z-mean delta `+0.168` | raw-mean delta `+0.004395`
  - `rectified_mean` contribution delta `-0.103` | z-mean delta `+0.011` | raw-mean delta `+0.000000`
  - `envelope_mean` contribution delta `-0.102` | z-mean delta `+0.012` | raw-mean delta `+0.000000`
  - `mean` contribution delta `-0.029` | z-mean delta `-0.027` | raw-mean delta `-0.000000`

## Interpretation

1. The repaired percentile-band scaffold is not the blocker anymore: selected rows are timing-matched across channels, so the pass28/pass29 difference is a real channel / feature-behavior difference.
2. `brux1` remains the shared unresolved subject. On both channels it stays below `n3`, but the gap is much smaller on `C4-P4` (`+0.012`) than on `EMG1-EMG2` (`+0.260`).
3. The EMG failure is harsher because `brux1` and especially `brux2` are still pulled down by hostile amplitude / crossing terms, while `n3` keeps support from control-favoring irregularity / burst features.
4. The C4 comparison-channel gain is concentrated in `brux2`: `zero_crossing_rate` becomes a large positive separator for `brux2` over `n3`, and the net `brux2 - n3` margin flips from negative on EMG to strongly positive on C4.
5. This preserves the EMG-first framing but sharpens the next validity target: the current open benchmark should explain or constrain the stubborn `brux1`-vs-`n3` overlap before trying larger models.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and do one compact audit or patch next on the shared `brux1`-vs-`n3` failure surface:
- safest: audit whether `n3`'s remaining support is concentrated in one narrow feature family (`sample_entropy`, `burst_fraction`, `envelope_cv`) across both channels,
- higher-upside but still bounded: rerun the same scaffold with one tiny cross-channel exclusion set targeted only at the recurring `n3`-favoring family, then compare whether `brux1` finally clears `n3` without breaking `brux2`.

The safer next move is the first one because this pass shows the project is now blocked more by one stubborn subject/control overlap than by global scaffold validity.
