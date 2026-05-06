---
title: Bruxism CAP tiny-subject benchmarking upgrade
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../concepts/bruxism-cap.md
  - ../../projects/bruxism-cap/reports/literature-tiny-subject-benchmarking-upgrade-2026-05-05.md
---

# Bruxism CAP tiny-subject benchmarking upgrade

Question: after `pass36` through `pass40`, what one literature-backed benchmark/reporting upgrade best fits the current tiny subject-level CAP scaffold without broadening the project?

## Repo-grounded answer

Keep the current leakage-aware scaffold and make the benchmark contract more honest, not more complicated. The methodology scan supports keeping grouped `LOSO` plus subject-level aggregation as the primary endpoint, while adding explicit tiny-sample uncertainty reporting on top of that endpoint. The smallest justified next patch is to report exact `95%` binomial confidence intervals for subject-level sensitivity and specificity alongside the existing subject counts and mean-score aggregation. [[bruxism-cap]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]]

## Why this fits the current repo

### 1. It reinforces the existing anti-leakage contract
The literature on grouped / hierarchical cross-validation and repeated-measures identity confounding supports the repo's current choice to treat random-window CV as a leakage reference surface and `LOSO` as the primary evaluation surface. That contract should stay fixed rather than reopening leaky or threshold-tuned headline metrics. [[bruxism-cap]]

### 2. It matches the real size of the honest benchmark
The current honest subject surface is often only `2` bruxism subjects and `3` controls. Literature on small-sample cross-validation and binomial interval estimation says these point estimates are inherently noisy and should not be presented naked. A subject-level sensitivity of `1/2` or a specificity of `3/3` sounds cleaner than it is unless the interval width is shown.

### 3. It stays lightweight
This patch does not require nested CV, learned calibration, a new model family, or a new dataset. It only strengthens the benchmark readout. That fits the repo's current posture: keep the scaffold fixed while learning the real limits of the tiny CAP subset.

## Exact contract changes motivated by the scan

- Keep `LOSO` subject-grouped validation as the primary benchmark surface.
- Keep subject-level aggregation as the primary honest endpoint and treat window-level results as secondary.
- Report raw subject counts behind subject sensitivity and specificity.
- Add exact `95%` binomial confidence intervals for those subject-level sensitivity and specificity estimates.
- Keep one fixed primary subject threshold for the headline result and label any threshold sweep as exploratory only.
- If a calibration-oriented extra is added later, prefer a tiny subject-level probabilistic summary such as Brier score over heavy post-hoc calibration machinery.

## What the scan rejects for now

- no nested CV
- no threshold optimization presented as a validated operating point
- no isotonic / Platt calibration on this tiny subject count
- no broad benchmark pivot justified only by reporting concerns

## One smallest next implementation

This reporting upgrade is now implemented in the lightweight pipeline. `projects/bruxism-cap/src/train_baseline.py` preserves the existing `subject_aggregation` shape but adds exact `95%` Clopper-Pearson and Wilson intervals for subject-level sensitivity and specificity, explicit subject-count payloads for both denominators, a lightweight subject-level Brier score, and a clearer per-subject probability alias (`mean_positive_probability`) alongside the older `mean_score` field. `projects/bruxism-cap/src/eval.py` now surfaces the subject-level interval-bearing summary inline, and `projects/bruxism-cap/README.md` documents the added calibration-lite outputs. [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]] [[bruxism-cap]]

## Exact files changed in the repo patch

- `projects/bruxism-cap/src/train_baseline.py`
- `projects/bruxism-cap/src/eval.py`
- `projects/bruxism-cap/README.md`

## What stayed intentionally unchanged

- no nested CV
- no threshold retuning
- no new model family
- no change to the primary subject threshold (`0.5`)
- no removal of the original `mean_score` field or existing window-level summaries

## Artifact

Detailed repo report: `projects/bruxism-cap/reports/literature-tiny-subject-benchmarking-upgrade-2026-05-05.md`
