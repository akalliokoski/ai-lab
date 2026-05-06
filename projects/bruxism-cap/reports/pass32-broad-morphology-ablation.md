# Pass 32 — broader morphology ablation on the repaired percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded matched rerun completed; removing one compact broader control-favoring family does **not** rescue the EMG-first benchmark. `EMG1-EMG2` still misses both bruxism subjects and remains below the current honest baseline, while the same ablation also destroys the useful `brux2` recovery on `C4-P4`.

## Why this experiment exists

Pass31 showed that the suspected narrow `n3`-favoring trio was real but too small to justify a trio-only patch. The safest next experiment was therefore one compact broader morphology exclusion set on the same repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold.

This pass makes exactly one primary increment:
- keep the same verified `5`-subject percentile-band scaffold from pass28/pass29
- keep `EMG1-EMG2` primary and `C4-P4` comparative
- keep the same `logreg` LOSO interpretation surface
- exclude one broader control-favoring feature family: `mean, max, ptp, zero_crossing_rate, sample_entropy, burst_fraction, envelope_cv`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass32_broad_morphology_ablation.py`
- EMG LOSO report: `projects/bruxism-cap/reports/loso-cv-pass32-emg-a1-pct10-90-broad-ablation.json`
- C4 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass32-c4-a1-pct10-90-broad-ablation.json`
- Summary JSON: `projects/bruxism-cap/reports/pass32-broad-morphology-ablation-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md`

## Matched-scaffold verification
- Selected rows are still timing-matched across channels: `True`.
- Shared columns checked: `subject_id, window_index, start_s, end_s, relative_time_quantile, time_match_rank`.
- The ablation therefore changes only the train-time feature set, not the repaired extraction scaffold.

## Feature selection
- Base exclusions preserved: `^bp_, ^rel_bp_, ^ratio_`
- New exact exclusions: `^(mean|max|ptp|zero_crossing_rate|sample_entropy|burst_fraction|envelope_cv)$`
- Remaining trainable feature count per channel: `10`
- Remaining features: `std, min, rms, line_length, rectified_mean, rectified_std, envelope_mean, envelope_std, burst_rate_hz, p95_abs`

## Honest LOSO subject-level result

### `EMG1-EMG2`
- baseline subject-level balanced accuracy: `0.333`
- ablation subject-level balanced accuracy: `0.333`
- baseline subject-level sensitivity: `0.000`
- ablation subject-level sensitivity: `0.000`
- baseline highest control vs best bruxism margin: `-0.260`
- ablation highest control vs best bruxism margin: `-0.224`
- subject score deltas:
- `brux1`: baseline `0.270` -> ablation `0.205` (delta `-0.065`) | predicted `control` -> `control`
- `brux2`: baseline `0.036` -> ablation `0.406` (delta `+0.371`) | predicted `control` -> `control`
- `n3`: baseline `0.530` -> ablation `0.630` (delta `+0.101`) | predicted `bruxism` -> `bruxism`
- `n5`: baseline `0.291` -> ablation `0.386` (delta `+0.095`) | predicted `control` -> `control`
- `n11`: baseline `0.325` -> ablation `0.444` (delta `+0.119`) | predicted `control` -> `control`

### `C4-P4`
- baseline subject-level balanced accuracy: `0.750`
- ablation subject-level balanced accuracy: `0.750`
- baseline subject-level sensitivity: `0.500`
- ablation subject-level sensitivity: `0.500`
- baseline `brux2 - n3` mean-score gap: `+0.542`
- ablation `brux2 - n3` mean-score gap: `-0.126`
- subject score deltas:
- `brux1`: baseline `0.405` -> ablation `0.635` (delta `+0.229`) | predicted `control` -> `bruxism`
- `brux2`: baseline `0.959` -> ablation `0.348` (delta `-0.611`) | predicted `bruxism` -> `control`
- `n3`: baseline `0.417` -> ablation `0.473` (delta `+0.056`) | predicted `control` -> `control`
- `n5`: baseline `0.212` -> ablation `0.454` (delta `+0.242`) | predicted `control` -> `control`
- `n11`: baseline `0.188` -> ablation `0.429` (delta `+0.242`) | predicted `control` -> `control`

## Key failure-surface checks

### `EMG1-EMG2`: `n3` still over `brux1`
- baseline `n3 - brux1` gap: `+0.260`
- ablation `n3 - brux1` gap: `+0.425`
- strongest surviving positive contributors toward `n3`:
  - `min` contribution delta `+6.997` | z-mean delta `+5.715` | raw-mean delta `+0.000105`
  - `envelope_std` contribution delta `+6.714` | z-mean delta `-15.644` | raw-mean delta `-0.000008`
  - `rectified_std` contribution delta `+3.768` | z-mean delta `-11.191` | raw-mean delta `-0.000011`
  - `line_length` contribution delta `+1.035` | z-mean delta `-0.761` | raw-mean delta `-0.005808`

### `C4-P4`: `brux2` no longer stays above `n3`
- baseline `brux2 - n3` gap: `+0.542`
- ablation `brux2 - n3` gap: `-0.126`
- strongest surviving negative contributors against `brux2`:
  - `burst_rate_hz` contribution delta `-0.343` | z-mean delta `+0.649` | raw-mean delta `+0.513333`
  - `rectified_mean` contribution delta `-0.132` | z-mean delta `+0.011` | raw-mean delta `+0.000000`
  - `envelope_mean` contribution delta `-0.129` | z-mean delta `+0.012` | raw-mean delta `+0.000000`

## Interpretation

1. The broader morphology exclusion set is **too destructive** to be the next honest EMG fix. It does not push `brux1` above `n3` on `EMG1-EMG2`, and it keeps both bruxism subjects below threshold.
2. The same ablation also breaks the most useful comparison-channel behavior: `C4-P4` loses the earlier `brux2` recovery and falls back toward a flat, low-confidence subject surface.
3. This preserves an important negative result: the recurring control-favoring family was diagnostically real, but removing it wholesale erases signal faster than it removes the transfer failure.
4. The remaining EMG-first bottleneck is therefore likely about **how** those morphology differences are represented or normalized, not just whether they are present.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and stay EMG-first.

The next safest experiment should be **validity-focused rather than another large deletion**:
- audit whether the remaining raw-amplitude dependence can be stabilized with a subject- or record-relative morphology representation on `EMG1-EMG2`, or
- test one smaller exclusion that leaves `zero_crossing_rate` and the core amplitude envelope intact while only removing the most extreme raw-location terms.

Do **not** promote this pass32 ablation as the new baseline; preserve it as a negative result.
