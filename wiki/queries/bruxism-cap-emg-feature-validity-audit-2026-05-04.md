---
title: Bruxism CAP EMG feature-validity audit (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, notes, research, dataset]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md
  - ../projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md
---

# Question
What exactly is driving the current `EMG1-EMG2` subject-score ordering failure on the matched `SLEEP-S2 + MCAP-A3-only` scaffold?

# Short answer
The failure is no longer best described as a threshold problem. It is now a small feature-validity problem inside the fixed matched EMG scaffold.

On the saved pass14 `logreg` LOSO rerun, the subject ordering stays:
- `n3` `0.267`
- `n5` `0.266`
- `brux1` `0.176`
- `n11` `0.095`
- `brux2` `0.074`

So the same two controls still outrank the best bruxism subject. [[bruxism-cap]] [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]]

# What the pass16 audit added
A new bounded audit rebuilt the pass14 LOSO `logreg` folds and decomposed which standardized features were pushing each held-out subject up or down.^[../projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md]

## Repeated control-favoring feature family
Among the controls that still score above `brux1`, the same small feature family recurs:
- `ratio_alpha_delta`
- `min`
- `sample_entropy`

Those features show up repeatedly among the top positive contributors for `n3` and `n5`, with `rel_bp_alpha` and sometimes `zero_crossing_rate` also helping. This is useful because it shrinks the next patch target from “improve EMG somehow” to “test one small feature-family change.” [[bruxism-cap]]

## `brux1` looks like a different failure surface
`brux1` is not just slightly worse on the same features. Its fold is dominated by extreme negative contributions from raw-scale absolute terms:
- `mean`
- `bp_theta`
- `bp_alpha`
- `ratio_theta_beta`
- `bp_delta`

That pattern suggests the current EMG recipe is mixing two problems:
1. a recurring control-favoring feature family in the honest high-score controls
2. unstable absolute-power / mean behavior for `brux1`

So a single threshold change was never going to fix this ranking. [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]] [[bruxism-cap]]

## `brux2` is not the same as `brux1`
The pass16 audit also preserved that `brux2` is a distinct failure mode. It is not just barely below the controls; it sits materially lower than every control except `n11`. That means one patch aimed only at lifting `brux1` may still leave `brux2` unresolved.

# Practical verdict
This is still a negative result, but it is a more useful negative result than pass15 alone.

The main repo-grounded lesson is:
- do **not** spend another pass on threshold schedules
- keep the matched `EMG1-EMG2 A3-only` scaffold fixed
- try one compact EMG feature-family ablation next

# Best next experiment
The safest next experiment is:
1. keep the same pass14 matched subset and LOSO path
2. drop the EEG-style relative bandpower / ratio family first
3. rerun the matched EMG `A3-only` baseline
4. check whether the subject ordering becomes less hostile to `brux1` without creating extra control positives

If that helps, the repo can then decide whether to replace that family with a more EMG-aligned burst / amplitude summary family instead of broadening the model class.
