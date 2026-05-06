# Pass 39 — bounded multi-feature record-relative scale-floor audit on the repaired EMG scaffold

Date: 2026-05-05
Status: bounded post-pass38 representation audit completed. Exactly one next earlier-stage increment was tested inside the pass34-style record-relative transform before the fixed pass35 shape merge: apply the same robust-scale floor `max(MAD, 0.5 * q90(|x - median|), 1e-06)` to `envelope_cv` plus one chosen stronger recurring offender, `mean`, while keeping selected rows, subject set, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Why `mean` was chosen over `rectified_std`

The pass36 fold audit shows that `mean` is the dominant recurring offender inside the remaining `brux1` suppression block, not just another member of the same family.

- Against `n5`, `mean` contributes `+46.576` to `n5 - brux1`, versus only `+3.797` from `rectified_std`.
- Against `n11`, `mean` contributes `+46.632` to `n11 - brux1`, versus only `+3.840` from `rectified_std`.
- The associated record-relative z-mean deltas are also much larger for `mean` (`-655.648` vs `-13.878` against `n5`; `-655.648` vs `-13.876` against `n11`).

So the strongest bounded follow-through after pass38 is to keep `envelope_cv` fixed and pair it with `mean`, because that tests the most dominant remaining contributor without broadening beyond one additional feature.

## Exact bounded change

- Start from the existing pass28 repaired `EMG1-EMG2` `A1-only` percentile-band feature CSV and rebuild the pass34 record-relative table.
- Keep the pass34 retained-feature list fixed: `mean, max, ptp, line_length, zero_crossing_rate, rectified_std, envelope_std, envelope_cv, rectified_mean, envelope_mean, p95_abs`.
- Keep pass35 shape merge fixed after the record-relative step.
- Override only `envelope_cv, mean` after the standard pass34 transform with: `z := (x - median_subject_feature) / max(MAD_subject_feature, 0.5 * q90(|x - median_subject_feature|), 1e-06)`.
- Leave every other retained feature and every evaluation setting unchanged.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass39_envelope_cv_mean_scale_floor_audit.py`
- Pass39 feature table: `projects/bruxism-cap/data/window_features_pass39_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_mean_floor.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass39-emg-a1-pct10-90-record-relative-shape-envcv-mean-floor.json`
- Summary JSON: `projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.md`

## Apples-to-apples comparison against unchanged pass36, pass37, and pass38

### Scaffold parity
- pass36 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass37 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass38 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass39 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- train-time exclusions unchanged: `['bp_delta', 'rel_bp_delta', 'bp_theta', 'rel_bp_theta', 'bp_alpha', 'rel_bp_alpha', 'bp_beta', 'rel_bp_beta', 'ratio_theta_beta', 'ratio_alpha_beta', 'ratio_alpha_delta']`
- pass39 modified transform features only: `['envelope_cv', 'mean']`

### Subject-level LOSO summary
- pass36 balanced accuracy: `0.750`
- pass37 balanced accuracy: `0.750`
- pass38 balanced accuracy: `0.750`
- pass39 balanced accuracy: `0.750`
- pass36 sensitivity: `0.500`
- pass37 sensitivity: `0.500`
- pass38 sensitivity: `0.500`
- pass39 sensitivity: `0.500`
- pass36 specificity: `1.000`
- pass37 specificity: `1.000`
- pass38 specificity: `1.000`
- pass39 specificity: `1.000`

Subject score deltas:
- `brux1`: pass36 `0.112` -> pass37 `0.118` -> pass38 `0.115` -> pass39 `0.114` | delta vs pass36 `+0.003` | delta vs pass37 `-0.003` | delta vs pass38 `-0.000` | predicted `control` -> `control`
- `brux2`: pass36 `0.808` -> pass37 `0.823` -> pass38 `0.806` -> pass39 `0.806` | delta vs pass36 `-0.002` | delta vs pass37 `-0.017` | delta vs pass38 `+0.000` | predicted `bruxism` -> `bruxism`
- `n3`: pass36 `0.068` -> pass37 `0.090` -> pass38 `0.067` -> pass39 `0.067` | delta vs pass36 `-0.001` | delta vs pass37 `-0.023` | delta vs pass38 `+0.000` | predicted `control` -> `control`
- `n5`: pass36 `0.385` -> pass37 `0.374` -> pass38 `0.386` -> pass39 `0.386` | delta vs pass36 `+0.001` | delta vs pass37 `+0.011` | delta vs pass38 `-0.000` | predicted `control` -> `control`
- `n11`: pass36 `0.489` -> pass37 `0.484` -> pass38 `0.490` -> pass39 `0.490` | delta vs pass36 `+0.002` | delta vs pass37 `+0.007` | delta vs pass38 `+0.000` | predicted `control` -> `control`

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: pass36 `2.14e-82` -> pass37 `2.23e-71` -> pass38 `4.61e-78` -> pass39 `3.79e-65`
- early ranks `1-3` amp/disp mean: pass36 `-205.274` -> pass37 `-169.619` -> pass38 `-194.660` -> pass39 `-162.058`
- pass39 mid ranks `4-7` mean score: `0.207`
- pass39 late ranks `8-10` mean score: `0.106`

Early-window detail:
- rank `1` | window `3` | start `3500s` | score pass36 `1.63e-97` -> pass37 `1.59e-74` -> pass38 `1.00e-92` -> pass39 `7.83e-77` | amp/disp pass36 `-227.752` -> pass37 `-174.211` -> pass38 `-216.524` -> pass39 `-179.931` | pass39 shape `+1.070` | pass39 other `+5.246`
- rank `2` | window `5` | start `3560s` | score pass36 `4.56e-84` -> pass37 `2.02e-72` -> pass38 `1.22e-79` -> pass39 `5.96e-66` | amp/disp pass36 `-196.537` -> pass37 `-169.091` -> pass38 `-186.132` -> pass39 `-154.612` | pass39 shape `+0.779` | pass39 other `+5.274`
- rank `3` | window `7` | start `4370s` | score pass36 `6.37e-82` -> pass37 `6.49e-71` -> pass38 `1.37e-77` -> pass39 `1.08e-64` | amp/disp pass36 `-191.532` -> pass37 `-165.555` -> pass38 `-181.325` -> pass39 `-151.631` | pass39 shape `+0.594` | pass39 other `+5.374`

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

- `brux1` moves from pass36 `0.112` to pass39 `0.114` (`+0.003`), versus pass37 `0.118` and pass38 `0.115`.
- `n3` on pass39 is `0.067`, so `brux1 - n3 = +0.048`.
- `n5` on pass39 is `0.386`, so `n5 - brux1 = +0.271`.
- `n11` on pass39 is `0.490`, so `n11 - brux1 = +0.376`.

## Verdict

This paired earlier-stage floor is still too weak to rescue `brux1` and does not beat the best prior bounded stabilization surface on the target subject.

Expanded read: Pass39 does not beat the best earlier bounded stabilization surface on `brux1` (`pass37` stays at `0.118` while pass39 reaches `0.114`), even though it remains apples-to-apples and preserves the repaired control verdict.

## Safest next bounded benchmark increment

Keep the same repaired five-subject scaffold and stay inside the same earlier-stage record-relative family, but swap the companion floor feature once: preserve the new `mean` result as evidence, then test the same bounded floor on `envelope_cv` plus `rectified_std` while keeping the pass35 shape merge, selected rows, and evaluation contract fixed.

## Explicitly rejected broader move

Rejected move: channel pivot, broad feature expansion, privacy implementation, or synthetic-data / LLM work.

Why rejected:
- this pass answers the exact next bounded record-relative question on the current EMG scaffold,
- the result still needs to be interpreted as a localized `brux1` stabilization read rather than a reason to broaden the benchmark frame,
- broadening now would blur whether the remaining failure is the residual earlier-stage amplitude construction or something introduced by an unrelated new branch.
