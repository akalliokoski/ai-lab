# Pass 38 — bounded envelope-CV robust-scale-floor audit on the repaired EMG scaffold

Date: 2026-05-05
Status: bounded post-pass37 representation audit completed. One tiny earlier-stage change was tested inside the pass34-style record-relative transform before the fixed pass35 shape merge: recompute only `envelope_cv` with the scale floor `max(MAD, 0.5 * q90(|x - median|), 1e-06)` while keeping selected rows, subject set, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Hypothesis

The remaining catastrophic early `brux1` collapse is not just a post-table outlier problem. Inside the pass34-style record-relative transform, `envelope_cv` appears to be over-amplified because its within-record `MAD` is too small relative to the same subject's sparse high-CV tail. If `envelope_cv` uses a bounded tail-aware robust-scale floor `max(MAD, 0.5 * q90(|x - median|))`, the early `brux1` trio should be penalized less aggressively without reopening the repaired `n3` / `n5` / `n11` control surface.

## Exact tiny change

- Start from the existing pass28 repaired `EMG1-EMG2` `A1-only` percentile-band feature CSV and rebuild the pass34 record-relative table.
- Keep the pass34 retained-feature list fixed: `mean, max, ptp, line_length, zero_crossing_rate, rectified_std, envelope_std, envelope_cv, rectified_mean, envelope_mean, p95_abs`.
- Keep pass35 shape merge fixed after the record-relative step.
- Override only `envelope_cv` after the standard pass34 transform with: `z := (x - median_subject_feature) / max(MAD_subject_feature, 0.5 * q90(|x - median_subject_feature|), 1e-06)`.
- Leave every other retained feature and every evaluation setting unchanged.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass38_envelope_cv_scale_floor_audit.py`
- Pass38 feature table: `projects/bruxism-cap/data/window_features_pass38_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcvfloor.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass38-emg-a1-pct10-90-record-relative-shape-envcvfloor.json`
- Summary JSON: `projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.md`

## Apples-to-apples comparison against unchanged pass36 and pass37

### Scaffold parity
- pass36 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass37 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- pass38 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- train-time exclusions unchanged: `['bp_delta', 'rel_bp_delta', 'bp_theta', 'rel_bp_theta', 'bp_alpha', 'rel_bp_alpha', 'bp_beta', 'rel_bp_beta', 'ratio_theta_beta', 'ratio_alpha_beta', 'ratio_alpha_delta']`
- pass38 modified transform feature only: `envelope_cv`

### Subject-level LOSO summary
- pass36 balanced accuracy: `0.750`
- pass37 balanced accuracy: `0.750`
- pass38 balanced accuracy: `0.750`
- pass36 sensitivity: `0.500`
- pass37 sensitivity: `0.500`
- pass38 sensitivity: `0.500`
- pass36 specificity: `1.000`
- pass37 specificity: `1.000`
- pass38 specificity: `1.000`

Subject score deltas:
- `brux1`: pass36 `0.112` -> pass37 `0.118` -> pass38 `0.115` | delta vs pass36 `+0.003` | delta vs pass37 `-0.003` | predicted `control` -> `control`
- `brux2`: pass36 `0.808` -> pass37 `0.823` -> pass38 `0.806` | delta vs pass36 `-0.002` | delta vs pass37 `-0.017` | predicted `bruxism` -> `bruxism`
- `n3`: pass36 `0.068` -> pass37 `0.090` -> pass38 `0.067` | delta vs pass36 `-0.001` | delta vs pass37 `-0.023` | predicted `control` -> `control`
- `n5`: pass36 `0.385` -> pass37 `0.374` -> pass38 `0.386` | delta vs pass36 `+0.001` | delta vs pass37 `+0.011` | predicted `control` -> `control`
- `n11`: pass36 `0.489` -> pass37 `0.484` -> pass38 `0.490` | delta vs pass36 `+0.002` | delta vs pass37 `+0.007` | predicted `control` -> `control`

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: pass36 `2.14e-82` -> pass37 `2.23e-71` -> pass38 `4.61e-78`
- early ranks `1-3` amp/disp mean: pass36 `-205.274` -> pass37 `-169.619` -> pass38 `-194.660`
- pass38 mid ranks `4-7` mean score: `0.207`
- pass38 late ranks `8-10` mean score: `0.105`

Early-window detail:
- rank `1` | window `3` | start `3500s` | score pass36 `1.63e-97` -> pass37 `1.59e-74` -> pass38 `1.00e-92` | amp/disp pass36 `-227.752` -> pass37 `-174.211` -> pass38 `-216.524` | pass38 shape `+1.070` | pass38 other `+5.246`
- rank `2` | window `5` | start `3560s` | score pass36 `4.56e-84` -> pass37 `2.02e-72` -> pass38 `1.22e-79` | amp/disp pass36 `-196.537` -> pass37 `-169.091` -> pass38 `-186.132` | pass38 shape `+0.779` | pass38 other `+5.274`
- rank `3` | window `7` | start `4370s` | score pass36 `6.37e-82` -> pass37 `6.49e-71` -> pass38 `1.37e-77` | amp/disp pass36 `-191.532` -> pass37 `-165.555` -> pass38 `-181.325` | pass38 shape `+0.594` | pass38 other `+5.374`

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

Only slightly, and not enough to beat the simpler pass37 clip.

- `brux1` rises from `0.112` on pass36 to `0.115` on pass38 (`+0.003`), so the earlier-stage floor helps a little.
- `n3` stays below `brux1` on pass38 (`brux1 - n3 = +0.048`), so the old `n3` reversal does not reopen.
- `n5` and `n11` stay above `brux1` by wide margins (`n5 - brux1 = +0.271`, `n11 - brux1 = +0.376`), so the control-side bottleneck is still active.
- Compared with pass37, pass38 is weaker on the target subject: `brux1` falls from `0.118` to `0.115` while `n5` and `n11` move back upward.

## Verdict

This earlier-stage robust-scale-floor idea is directionally compatible with the current scaffold, but it is too weak and too narrow to materially change the benchmark. It improves `brux1` slightly versus pass36 (`0.112` -> `0.115`) and preserves the repaired subject-level verdict (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity), but it does not beat the simpler pass37 post-table clip and it leaves the early `brux1` trio catastrophically close to zero. That means the remaining instability is probably not explained by `envelope_cv` scale alone.

## Safest next bounded benchmark increment

Keep the repaired five-subject scaffold fixed again, but stay inside the same record-relative amplitude family and widen only one notch beyond this single-feature floor. The safest next increment is to test one equally bounded multi-feature earlier-stage audit that applies the same style of robust-scale floor to `envelope_cv` together with one of the two stronger recurring offenders (`rectified_std` or `mean`), while keeping the pass35 shape merge, selected rows, and evaluation contract fixed.

## Explicitly rejected broader move

Rejected move: channel pivot, broad feature expansion, or privacy / LLM branch activation.

Why rejected:
- this audit kept the question narrow and shows the benchmark is still explainable on the current EMG scaffold,
- the result is informative but small, so broadening now would blur whether the remaining failure is a single-feature scale issue or a slightly wider record-relative amplitude construction issue,
- pass38 does not deliver a stabilization handoff point yet, so the future branches should remain gated.
