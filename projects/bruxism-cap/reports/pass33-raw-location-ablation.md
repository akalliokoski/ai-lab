# Pass 33 — smaller raw-location ablation on the repaired percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded matched rerun completed; removing only the most extreme raw-location terms does **not** rescue the EMG-first benchmark. `EMG1-EMG2` still misses both bruxism subjects and falls farther below the current honest baseline, while the same smaller ablation leaves the useful `C4-P4` `brux2` recovery essentially unchanged.

## Why this experiment exists

Pass32 showed that the broader morphology ablation was too destructive. The next safer follow-up suggested by the repo evidence was one smaller exclusion that keeps `zero_crossing_rate` and the core amplitude-envelope family intact while removing only the most extreme raw-location terms.

This pass makes exactly one primary increment:
- keep the same verified `5`-subject percentile-band scaffold from pass28/pass29
- keep `EMG1-EMG2` primary and `C4-P4` comparative
- keep the same `logreg` LOSO interpretation surface
- exclude only one small raw-location family: `mean, min, max`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`
- EMG LOSO report: `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`
- C4 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`
- Summary JSON: `projects/bruxism-cap/reports/pass33-raw-location-ablation-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass33-raw-location-ablation.md`

## Matched-scaffold verification
- Selected rows are still timing-matched across channels: `True`.
- Shared columns checked: `subject_id, window_index, start_s, end_s, relative_time_quantile, time_match_rank`.
- The ablation therefore changes only the train-time feature set, not the repaired extraction scaffold.

## Feature selection
- Base exclusions preserved: `^bp_, ^rel_bp_, ^ratio_`
- New exact exclusions: `^(mean|min|max)$`
- Remaining trainable feature count per channel: `14`
- Remaining features: `std, ptp, rms, line_length, zero_crossing_rate, sample_entropy, rectified_mean, rectified_std, envelope_mean, envelope_std, envelope_cv, burst_fraction, burst_rate_hz, p95_abs`

## Honest LOSO subject-level result

### `EMG1-EMG2`
- baseline subject-level balanced accuracy: `0.333`
- ablation subject-level balanced accuracy: `0.333`
- baseline subject-level sensitivity: `0.000`
- ablation subject-level sensitivity: `0.000`
- baseline highest control vs best bruxism margin: `-0.260`
- ablation highest control vs best bruxism margin: `-0.492`
- subject score deltas:
- `brux1`: baseline `0.270` -> ablation `0.030` (delta `-0.240`) | predicted `control` -> `control`
- `brux2`: baseline `0.036` -> ablation `0.035` (delta `-0.001`) | predicted `control` -> `control`
- `n3`: baseline `0.530` -> ablation `0.527` (delta `-0.003`) | predicted `bruxism` -> `bruxism`
- `n5`: baseline `0.291` -> ablation `0.291` (delta `-0.001`) | predicted `control` -> `control`
- `n11`: baseline `0.325` -> ablation `0.327` (delta `+0.002`) | predicted `control` -> `control`

### `C4-P4`
- baseline subject-level balanced accuracy: `0.750`
- ablation subject-level balanced accuracy: `0.750`
- baseline subject-level sensitivity: `0.500`
- ablation subject-level sensitivity: `0.500`
- baseline `brux2 - n3` mean-score gap: `+0.542`
- ablation `brux2 - n3` mean-score gap: `+0.544`
- subject score deltas:
- `brux1`: baseline `0.405` -> ablation `0.403` (delta `-0.003`) | predicted `control` -> `control`
- `brux2`: baseline `0.959` -> ablation `0.959` (delta `+0.000`) | predicted `bruxism` -> `bruxism`
- `n3`: baseline `0.417` -> ablation `0.415` (delta `-0.002`) | predicted `control` -> `control`
- `n5`: baseline `0.212` -> ablation `0.212` (delta `-0.000`) | predicted `control` -> `control`
- `n11`: baseline `0.188` -> ablation `0.187` (delta `-0.000`) | predicted `control` -> `control`

## Key failure-surface checks

### `EMG1-EMG2`: `n3` still over `brux1`
- baseline `n3 - brux1` gap: `+0.260`
- ablation `n3 - brux1` gap: `+0.497`
- strongest surviving positive contributors toward `n3`:
  - `ptp` contribution delta `+2.561` | z-mean delta `-10.722` | raw-mean delta `-0.000389`
  - `zero_crossing_rate` contribution delta `+2.475` | z-mean delta `+0.975` | raw-mean delta `+0.060583`
  - `envelope_std` contribution delta `+1.673` | z-mean delta `-15.644` | raw-mean delta `-0.000008`
  - `line_length` contribution delta `+1.153` | z-mean delta `-0.761` | raw-mean delta `-0.005808`
  - `rectified_std` contribution delta `+0.650` | z-mean delta `-11.191` | raw-mean delta `-0.000011`
  - `envelope_cv` contribution delta `+0.432` | z-mean delta `-4.445` | raw-mean delta `-0.711137`

### `C4-P4`: `brux2` stays above `n3`
- baseline `brux2 - n3` gap: `+0.542`
- ablation `brux2 - n3` gap: `+0.544`
- strongest surviving negative contributors against `brux2`:
  - `burst_rate_hz` contribution delta `-0.220` | z-mean delta `+0.649` | raw-mean delta `+0.513333`
  - `burst_fraction` contribution delta `-0.182` | z-mean delta `+0.168` | raw-mean delta `+0.004395`
  - `rectified_mean` contribution delta `-0.101` | z-mean delta `+0.011` | raw-mean delta `+0.000000`
  - `envelope_mean` contribution delta `-0.100` | z-mean delta `+0.012` | raw-mean delta `+0.000000`
  - `p95_abs` contribution delta `-0.023` | z-mean delta `-0.114` | raw-mean delta `-0.000001`
  - `std` contribution delta `-0.015` | z-mean delta `-0.013` | raw-mean delta `-0.000000`

## Interpretation

1. The smaller raw-location ablation is **not** a useful EMG fix: `EMG1-EMG2` keeps both bruxism subjects below threshold and makes the best-bruxism-versus-highest-control margin markedly worse.
2. The EMG surface does not improve in a mixed way here; it mostly collapses `brux1` (`0.270` -> `0.030`) while leaving `n3` essentially unchanged (`0.530` -> `0.527`), so the remaining failure is still the same `n3 > brux1` ordering problem on the repaired scaffold.
3. The `C4-P4` comparison surface is nearly unchanged, which is also informative: this tiny deletion removes something EMG still needs while not meaningfully altering the stronger comparison-channel behavior.
4. This preserves a narrower negative result: the repo evidence now suggests the problem is not just a few raw-location features being present, but how morphology is represented fold-by-fold once subjects are held out.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and stay EMG-first.

The next safest experiment should stay validity-focused rather than stack another broad deletion:
- audit whether the remaining morphology features should be converted into a record-relative or within-subject-relative representation before training, or
- run one matched audit that compares raw versus within-record standardized versions of the retained amplitude-envelope family without changing the selector or model family.

Do **not** promote this pass33 ablation as the new baseline; preserve it as a negative result.
