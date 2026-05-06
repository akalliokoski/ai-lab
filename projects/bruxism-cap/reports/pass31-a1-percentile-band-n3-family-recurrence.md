# Pass 31 — recurrence audit of the suspected `n3`-favoring family on the matched percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded cross-channel validity audit completed; the suspected narrow `n3`-favoring family (`sample_entropy`, `burst_fraction`, `envelope_cv`) does recur, but it does **not** dominate the repaired scaffold across both channels. The harder EMG `n3` advantage is still driven more by broader amplitude / crossing features, so a tiny family-only ablation would be under-justified as the next primary experiment.

## Why this audit exists

Pass30 suggested a cautious next question rather than a new model change:
- keep the repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed
- keep `EMG1-EMG2` primary and `C4-P4` comparative
- test whether the remaining `n3` support is really concentrated in one small feature family before patching the training surface

This pass makes exactly one primary increment:
- reuse the same matched pass28/pass29 rows and the same train-time exclusions
- keep the same LOSO `logreg` audit surface
- quantify how much of the positive `n3` gap is explained by the suspected family versus the full surviving feature set

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`
- Audit report: `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md`
- Matched EMG feature CSV: `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- Matched C4 feature CSV: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`

## Matched-scaffold verification
- Selected rows are still timing-matched across channels: `True`.
- Shared columns checked: `subject_id, window_index, start_s, end_s, relative_time_quantile, time_match_rank`.
- This audit therefore stays on the same repaired percentile-band scaffold and isolates feature-behavior interpretation rather than extraction drift.

## Reproduced subject orderings

### `EMG1-EMG2`
- `n3` (control): mean LOSO score `0.530` | positive-window fraction `0.800`
- `n11` (control): mean LOSO score `0.325` | positive-window fraction `0.100`
- `n5` (control): mean LOSO score `0.291` | positive-window fraction `0.000`
- `brux1` (bruxism): mean LOSO score `0.270` | positive-window fraction `0.000`
- `brux2` (bruxism): mean LOSO score `0.036` | positive-window fraction `0.000`

### `C4-P4`
- `brux2` (bruxism): mean LOSO score `0.959` | positive-window fraction `1.000`
- `n3` (control): mean LOSO score `0.417` | positive-window fraction `0.400`
- `brux1` (bruxism): mean LOSO score `0.405` | positive-window fraction `0.300`
- `n5` (control): mean LOSO score `0.212` | positive-window fraction `0.000`
- `n11` (control): mean LOSO score `0.188` | positive-window fraction `0.100`

## Family-share results

### `EMG1-EMG2`: `n3` over `brux1`
- score gap: `+0.260`
- total positive contribution toward `n3`: `164.690`
- suspected-family positive contribution: `0.443`
- suspected-family share of the positive `n3` gap: `0.269%`
- top positive features overall:
  - `mean` contribution delta `+156.609` | z-mean delta `-114.418` | raw-mean delta `-0.000001`
  - `max` contribution delta `+1.825` | z-mean delta `-15.420` | raw-mean delta `-0.000283`
  - `ptp` contribution delta `+1.414` | z-mean delta `-10.722` | raw-mean delta `-0.000389`
  - `zero_crossing_rate` contribution delta `+1.348` | z-mean delta `+0.975` | raw-mean delta `+0.060583`
  - `line_length` contribution delta `+1.138` | z-mean delta `-0.761` | raw-mean delta `-0.005808`
  - `min` contribution delta `+0.831` | z-mean delta `+5.715` | raw-mean delta `+0.000105`
  - `envelope_std` contribution delta `+0.803` | z-mean delta `-15.644` | raw-mean delta `-0.000008`
  - `burst_fraction` contribution delta `+0.341` | z-mean delta `+1.340` | raw-mean delta `+0.030788`
- suspected-family feature rows:
  - `burst_fraction` contribution delta `+0.341` | z-mean delta `+1.340` | raw-mean delta `+0.030788`
  - `sample_entropy` contribution delta `-0.302` | z-mean delta `+3.257` | raw-mean delta `+0.515308`
  - `envelope_cv` contribution delta `+0.102` | z-mean delta `-4.445` | raw-mean delta `-0.711137`

### `EMG1-EMG2`: `n3` over `brux2`
- score gap: `+0.494`
- total positive contribution toward `n3`: `3.810`
- suspected-family positive contribution: `0.394`
- suspected-family share of the positive `n3` gap: `10.333%`
- top positive features overall:
  - `zero_crossing_rate` contribution delta `+2.417` | z-mean delta `-4.054` | raw-mean delta `-0.203114`
  - `line_length` contribution delta `+0.992` | z-mean delta `-0.711` | raw-mean delta `-0.005340`
  - `burst_fraction` contribution delta `+0.386` | z-mean delta `+0.475` | raw-mean delta `+0.014258`
  - `min` contribution delta `+0.008` | z-mean delta `+0.094` | raw-mean delta `+0.000007`
  - `envelope_cv` contribution delta `+0.007` | z-mean delta `-0.175` | raw-mean delta `-0.087651`
- suspected-family feature rows:
  - `burst_fraction` contribution delta `+0.386` | z-mean delta `+0.475` | raw-mean delta `+0.014258`
  - `sample_entropy` contribution delta `-0.042` | z-mean delta `+0.169` | raw-mean delta `+0.069435`
  - `envelope_cv` contribution delta `+0.007` | z-mean delta `-0.175` | raw-mean delta `-0.087651`

### `C4-P4`: `n3` over `brux1`
- score gap: `+0.012`
- total positive contribution toward `n3`: `6.945`
- suspected-family positive contribution: `0.721`
- suspected-family share of the positive `n3` gap: `10.386%`
- top positive features overall:
  - `max` contribution delta `+4.287` | z-mean delta `-26.895` | raw-mean delta `-0.000273`
  - `mean` contribution delta `+1.339` | z-mean delta `-6.871` | raw-mean delta `-0.000001`
  - `envelope_cv` contribution delta `+0.562` | z-mean delta `-3.939` | raw-mean delta `-0.528116`
  - `zero_crossing_rate` contribution delta `+0.266` | z-mean delta `+0.033` | raw-mean delta `+0.000306`
  - `burst_rate_hz` contribution delta `+0.252` | z-mean delta `+1.109` | raw-mean delta `+0.803333`
  - `sample_entropy` contribution delta `+0.152` | z-mean delta `+2.370` | raw-mean delta `+0.467504`
  - `envelope_std` contribution delta `+0.080` | z-mean delta `-6.086` | raw-mean delta `-0.000008`
  - `burst_fraction` contribution delta `+0.008` | z-mean delta `+1.557` | raw-mean delta `+0.027161`
- suspected-family feature rows:
  - `envelope_cv` contribution delta `+0.562` | z-mean delta `-3.939` | raw-mean delta `-0.528116`
  - `sample_entropy` contribution delta `+0.152` | z-mean delta `+2.370` | raw-mean delta `+0.467504`
  - `burst_fraction` contribution delta `+0.008` | z-mean delta `+1.557` | raw-mean delta `+0.027161`

### `C4-P4`: `n3` over `brux2`
- score gap: `-0.542`
- total positive contribution toward `n3`: `0.689`
- suspected-family positive contribution: `0.182`
- suspected-family share of the positive `n3` gap: `26.372%`
- top positive features overall:
  - `burst_rate_hz` contribution delta `+0.219` | z-mean delta `-0.649` | raw-mean delta `-0.513333`
  - `burst_fraction` contribution delta `+0.182` | z-mean delta `-0.168` | raw-mean delta `-0.004395`
  - `rectified_mean` contribution delta `+0.103` | z-mean delta `-0.011` | raw-mean delta `-0.000000`
  - `envelope_mean` contribution delta `+0.102` | z-mean delta `-0.012` | raw-mean delta `-0.000000`
  - `mean` contribution delta `+0.029` | z-mean delta `+0.027` | raw-mean delta `+0.000000`
  - `p95_abs` contribution delta `+0.024` | z-mean delta `+0.114` | raw-mean delta `+0.000001`
  - `std` contribution delta `+0.016` | z-mean delta `+0.013` | raw-mean delta `+0.000000`
  - `rms` contribution delta `+0.016` | z-mean delta `+0.013` | raw-mean delta `+0.000000`
- suspected-family feature rows:
  - `burst_fraction` contribution delta `+0.182` | z-mean delta `-0.168` | raw-mean delta `-0.004395`
  - `sample_entropy` contribution delta `-0.130` | z-mean delta `-0.076` | raw-mean delta `-0.027182`
  - `envelope_cv` contribution delta `-0.066` | z-mean delta `+0.170` | raw-mean delta `+0.064475`

## Cross-channel recurrence of the suspected family
- `burst_fraction`: positive in `4/4` contrasts | negative in `0/4` | net contribution delta `+0.917`
- `envelope_cv`: positive in `3/4` contrasts | negative in `1/4` | net contribution delta `+0.605`
- `sample_entropy`: positive in `1/4` contrasts | negative in `3/4` | net contribution delta `-0.322`

## Interpretation

1. The suspected family is **real but not sufficient**. It shows up repeatedly, but not as the dominant explanation of the repaired scaffold across both channels.
2. The harsher EMG failure surface is broader than `sample_entropy + burst_fraction + envelope_cv`: the biggest positive support for `n3` still comes from wider amplitude / shape / crossing terms, so a family-only ablation would risk underfitting the actual gap.
3. The C4 comparison result is also not a clean family story. `envelope_cv` does recur, but the shared `brux1 < n3` gap on `C4-P4` is still mostly about larger non-family contributors.
4. This is therefore a useful negative audit against over-narrowing the next patch. The repo should preserve the suspected family as part of the story, but not mistake it for the whole explanation.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and stay EMG-first.

The safest next experiment is now:
- rerun the matched pass28/pass29 scaffold with one **broader but still compact** exclusion family focused on the recurring control-favoring morphology terms (`mean`, `max`, `ptp`, `zero_crossing_rate`, plus the previously suspected trio),
- then compare whether `brux1` clears `n3` on `EMG1-EMG2` without erasing the useful `brux2` behavior on `C4-P4`.

That is better justified than a trio-only ablation because this audit shows the control advantage is not concentrated narrowly enough for the smaller patch to be trusted.
