---
title: Bruxism CAP EMG envelope replacement family (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md
  - ../projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md
---

# Question
Did adding one compact EMG-oriented envelope / burst family improve the matched `EMG1-EMG2` `A3-only` CAP baseline on the verified 5-subject subset?

# Short answer
No. The first replacement-oriented EMG feature patch was a useful negative result, not a baseline win.

It did slightly recover both bruxism subject scores relative to the pass17 time-only ablation, and it reduced the worst `n3` control score relative to pass17, but it still failed the honest subject-level criterion and still did not beat the earlier pass14 full-feature EMG run. [[bruxism-cap]] [[bruxism-cap-emg-time-only-ablation-2026-05-04]]

# What changed
The repo added one compact EMG-oriented family to `projects/bruxism-cap/src/features.py` and regenerated the same matched `EMG1-EMG2` / exclusive `SLEEP-S2 + MCAP-A3-only` scaffold:
- `rectified_mean`
- `rectified_std`
- `envelope_mean`
- `envelope_std`
- `envelope_cv`
- `burst_fraction`
- `burst_rate_hz`
- `p95_abs`

The matched scaffold itself stayed fixed:
- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- windows per subject: `14`
- channel: `EMG1-EMG2`
- rule: exclusive `SLEEP-S2 + MCAP-A3-only`

# Main result

## Honest LOSO metrics still did not improve
Best LOSO `logreg` window-level balanced accuracy moved:
- pass14 full features: `0.629`
- pass17 time-only ablation: `0.614`
- pass18 envelope / burst replacement family: `0.600`

Subject-level aggregation stayed unchanged at the honest decision surface:
- balanced accuracy: `0.500`
- sensitivity: `0.000`
- specificity: `1.000`

So the new feature family did **not** rescue held-out bruxism subject detection. [[bruxism-cap]]

## Subject score ordering remained wrong
Pass18 `logreg` subject scores were:
- `n5` (`control`): `0.267`
- `n3` (`control`): `0.245`
- `brux1` (`bruxism`): `0.158`
- `n11` (`control`): `0.104`
- `brux2` (`bruxism`): `0.092`

Compared with pass17, this is directionally mixed rather than cleanly bad:
- `brux1` improved from `0.148` to `0.158`
- `brux2` improved from `0.055` to `0.092`
- `n3` dropped from `0.328` to `0.245`
- but `n5` rose back to `0.267`, still above `brux1`

That means the control-vs-bruxism ordering is still not good enough for the honest baseline criterion.

# What the follow-up audit teaches
The pass18 follow-up audit shows that the new EMG-oriented features were not ignored:
- `burst_rate_hz`, `envelope_cv`, `burst_fraction`, and `envelope_std` appear in top contributors

But the failure mechanism did not really disappear:
- high-score controls still recur through a small family including `min`, `sample_entropy`, and some envelope/burst terms
- `brux1` is still dominated by very large negative contributions from `mean`, `bp_theta`, `bp_alpha`, and `ratio_theta_beta`

So the project is now learning a more specific lesson: **adding EMG-style summaries is not enough if the old EEG-shaped family still dominates the same folds**. [[bruxism-cap-emg-feature-validity-audit-2026-05-04]] [[bruxism-cap-emg-time-only-ablation-2026-05-04]]

# Practical verdict
This pass does not beat the current best honest baseline.

The current best honest baseline is still the matched `C4-P4` exclusive `A1-only` pass12 result, because it is still the only run in this line that achieves subject-level sensitivity `0.500` without losing specificity. [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

# Best next bounded experiment
Keep the exact same matched `EMG1-EMG2 A3-only` scaffold and the new pass18 table, but make the next train-time change **selection-aware** instead of add-only:
- keep the new EMG family
- exclude `bp_*`, `rel_bp_*`, and `ratio_*` during training on the pass18 table
- compare directly against pass14, pass17, and pass18

That would answer the sharper question now: whether the new envelope / burst family helps only when the older EEG-shaped spectral family is no longer allowed to dominate the decision surface.