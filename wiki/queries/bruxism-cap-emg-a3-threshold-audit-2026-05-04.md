---
title: Bruxism CAP EMG1-EMG2 A3-only threshold audit on matched subset (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md
  - ../projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md
  - ../projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json
---

# Question
Does the stronger current EMG run (`EMG1-EMG2` with exclusive `SLEEP-S2 + MCAP-A3-only`) fail mainly because the subject threshold is too high, or because the subject-score ordering itself is wrong?

# Short answer
It fails because the **score ordering is wrong**, not because `0.5` is too strict.

Lowering the subject threshold can recover `brux1`, but only by also flipping `n3` and `n5` positive. Lowering it enough to recover both `brux1` and `brux2` predicts every subject positive. So the current saved EMG score surface has no threshold that improves the honest baseline over the default `0.5` rule. [[bruxism-cap]] [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

# Core evidence

## Current EMG A3-only subject ranking
- `n3` control: `0.267`
- `n5` control: `0.266`
- `brux1` bruxism: `0.176`
- `n11` control: `0.095`
- `brux2` bruxism: `0.074`

Two controls outrank the best bruxism subject, so threshold tuning cannot rescue the run cleanly.

## Threshold behavior
- Default `0.5`: sensitivity `0.000`, specificity `1.000`, balanced accuracy `0.500`
- Best zero-false-positive threshold: still sensitivity `0.000`, specificity `1.000`, balanced accuracy `0.500`
- Best threshold with any positive sensitivity: sensitivity `0.500`, specificity `0.333`, balanced accuracy `0.417`
- Thresholds that recover both bruxism subjects collapse to specificity `0.000`

## Honest anchor comparison
The current pass12 `C4-P4 A1-only` anchor still has a clean positive-vs-control margin:
- best bruxism minus highest control = `+0.362`

The current EMG A3-only run does not:
- best bruxism minus highest control = `-0.091`

That is the sharper reason the anchor still wins. [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]] [[bruxism-better-project-and-data-options-2026-05-04]]

# Updated interpretation
- The EMG-first direction still stands, because the audit explains *why* the current transfer fails instead of just reporting another miss.
- The next bottleneck is not subject-threshold choice.
- The next bottleneck is feature validity / score ordering on the matched EMG scaffold.
- The next bounded move should therefore be one EMG-focused feature audit, not more threshold tweaking and not a larger model.

# Best next bounded experiment
Run one compact feature-validity audit on the pass14 matched subset:
- compare per-subject feature summaries for `brux1`, `brux2`, `n3`, and `n5`
- identify which current handcrafted features are lifting `n3` / `n5` above `brux1`
- only then test one small EMG-aligned feature patch on the same fixed matched subset
