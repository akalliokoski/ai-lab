# Pass 40 — final bounded `envelope_cv + rectified_std` record-relative floor follow-through on the repaired EMG scaffold

Date: 2026-05-05
Status: completed. This is the last same-family earlier-stage follow-through after pass39 on the repaired five-subject percentile-band `EMG1-EMG2` `A1-only` scaffold. The only primary increment was to apply the same bounded robust-scale floor `max(MAD, 0.5 * q90(|x - median|), 1e-06)` to `envelope_cv + rectified_std` inside the pass34-style record-relative transform, while keeping the pass35 shape merge, selected rows, subject set, train-time exclusions, model family, and evaluation contract fixed.

## Why this pass exists

Pass39 already answered the stronger-offender question: `mean` was the right harsher companion to test first, and `envelope_cv + mean` softened the catastrophic early `brux1` trio more than pass38. But pass39 still did not beat pass37 on `brux1`, so one last apples-to-apples same-family follow-through was to swap only the companion feature and test `envelope_cv + rectified_std` without changing anything else.

Preserved pass39 lesson:
- `mean` remains the stronger offender diagnostically; pass40 is not a reversal of that conclusion.
- Pass39 beat pass38 on early-trio softening (`-194.660` -> `-162.058` amp/disp mean) but still failed to beat pass37 on subject-level `brux1` (`0.115` and `0.114` vs `0.118`).
- So pass40 is strictly a final same-family follow-through, not a new broad direction.

## Exact bounded change

- Start from the existing pass28 repaired `EMG1-EMG2` `A1-only` percentile-band feature CSV and rebuild the pass34 record-relative table.
- Keep the pass34 retained-feature list fixed: `mean, max, ptp, line_length, zero_crossing_rate, rectified_std, envelope_std, envelope_cv, rectified_mean, envelope_mean, p95_abs`.
- Keep the pass35 compact shape merge fixed after the record-relative step.
- Override only `envelope_cv` and `rectified_std` after the standard pass34 transform with: `z := (x - median_subject_feature) / max(MAD_subject_feature, 0.5 * q90(|x - median_subject_feature|), 1e-06)`.
- Leave every other retained feature and every evaluation setting unchanged.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass40_envelope_cv_rectified_std_scale_floor_audit.py`
- Pass40 feature table: `projects/bruxism-cap/data/window_features_pass40_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_rectstd_floor.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass40-emg-a1-pct10-90-record-relative-shape-envcv-rectstd-floor.json`
- Summary JSON: `projects/bruxism-cap/reports/pass40-envelope-cv-rectified-std-scale-floor-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass40-envelope-cv-rectified-std-scale-floor-audit.md`

## Apples-to-apples comparison against unchanged pass36 / pass37 / pass38 / pass39

### Scaffold parity
- pass36 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass37 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass38 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass39 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass40 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- train-time exclusions unchanged: `['bp_delta', 'rel_bp_delta', 'bp_theta', 'rel_bp_theta', 'bp_alpha', 'rel_bp_alpha', 'bp_beta', 'rel_bp_beta', 'ratio_theta_beta', 'ratio_alpha_beta', 'ratio_alpha_delta']`
- pass40 modified transform features only: `['envelope_cv', 'rectified_std']`

### Subject-level LOSO summary
- pass36 balanced accuracy: `0.750`
- pass37 balanced accuracy: `0.750`
- pass38 balanced accuracy: `0.750`
- pass39 balanced accuracy: `0.750`
- pass40 balanced accuracy: `0.750`
- pass36 sensitivity: `0.500`
- pass37 sensitivity: `0.500`
- pass38 sensitivity: `0.500`
- pass39 sensitivity: `0.500`
- pass40 sensitivity: `0.500`
- pass36 specificity: `1.000`
- pass37 specificity: `1.000`
- pass38 specificity: `1.000`
- pass39 specificity: `1.000`
- pass40 specificity: `1.000`

Subject score deltas:
- `brux1`: pass36 `0.112` -> pass37 `0.118` -> pass38 `0.115` -> pass39 `0.114` -> pass40 `0.112` | delta vs pass36 `+0.000` | delta vs pass37 `-0.006` | delta vs pass38 `-0.003`
- `brux2`: pass36 `0.808` -> pass37 `0.823` -> pass38 `0.806` -> pass39 `0.806` -> pass40 `0.836` | delta vs pass36 `+0.028` | delta vs pass37 `+0.013` | delta vs pass38 `+0.030`
- `n3`: pass36 `0.068` -> pass37 `0.090` -> pass38 `0.067` -> pass39 `0.067` -> pass40 `0.106` | delta vs pass36 `+0.038` | delta vs pass37 `+0.017` | delta vs pass38 `+0.040`
- `n5`: pass36 `0.385` -> pass37 `0.374` -> pass38 `0.386` -> pass39 `0.386` -> pass40 `0.373` | delta vs pass36 `-0.012` | delta vs pass37 `-0.002` | delta vs pass38 `-0.013`
- `n11`: pass36 `0.489` -> pass37 `0.484` -> pass38 `0.490` -> pass39 `0.490` -> pass40 `0.472` | delta vs pass36 `-0.016` | delta vs pass37 `-0.011` | delta vs pass38 `-0.018`

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: pass36 `2.14e-82` -> pass37 `2.23e-71` -> pass38 `4.61e-78` -> pass39 `3.79e-65` -> pass40 `9.10e-73`
- early ranks `1-3` amp/disp mean: pass36 `-205.274` -> pass37 `-169.619` -> pass38 `-194.660` -> pass39 `-162.058` -> pass40 `-182.086`
- pass40 mid ranks `4-7` mean score: `0.200`
- pass40 late ranks `8-10` mean score: `0.106`

Interpretation of the trio:
- pass40 softens the catastrophic early trio relative to pass36 and pass38, but not as much as pass39 and nowhere near enough to become threshold-relevant.
- So `rectified_std` does participate in the localized collapse, but it is weaker than the pass39 `mean` companion as a bounded fix.

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

Only minimally, and not enough to matter.

- `brux1` is effectively flat versus pass36: `0.112` -> `0.112` (`+0.000`).
- `brux1` is worse than both pass37 and pass39 on the target subject (`0.118` and `0.114` vs `0.112`).
- `n3` does not reopen as a formal reversal, but the margin shrinks sharply to `brux1 - n3 = +0.006`.
- `n5` and `n11` remain above `brux1` by wide margins: `n5 - brux1 = +0.261`, `n11 - brux1 = +0.361`.
- No control flips positive, and subject-level specificity remains `1.000`.

## Verdict

Pass40 closes the final same-family floor follow-through as another bounded negative result.

Expanded read:
- Pass39 preserved the important diagnostic conclusion that `mean` was the stronger offender to test first.
- Swapping the companion feature to `rectified_std` does not improve `brux1` meaningfully (`0.112` -> `0.112`) and does not beat pass37 (`0.118`) or pass39 (`0.114`).
- The repaired control surface stays intact enough to preserve the same honest subject-level verdict (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity), but the `brux1` bottleneck remains unresolved.

## Safest next bounded benchmark increment

Stop this exact `envelope_cv` floor-family subloop and preserve pass37 as the safest bounded stabilization surface inside the current scaffold. The next bounded increment should be one new representation question outside this exact companion-floor family, because pass38, pass39, and pass40 together now show that earlier-stage floor tweaks can soften the collapse directionally but do not resolve the benchmark.

## Explicitly rejected broader move

Rejected move: channel pivot, broad feature expansion, privacy implementation, or synthetic-data / LLM work.

Why rejected:
- pass40 is still a localized benchmark read on the same repaired EMG scaffold,
- it closes the exact same-family follow-through rather than opening a new branch,
- broadening now would hide the real lesson, which is that this floor family has been tested enough and still does not rescue `brux1`.
