---
title: Bruxism CAP pass42/pass44 cross-family methodology review
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../../projects/bruxism-cap/reports/methodology-review-pass42-pass44-cross-family-upgrade-2026-05-05.md
  - ../../projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.md
  - ../concepts/bruxism-cap.md
---

# Bruxism CAP pass42/pass44 cross-family methodology review

Question: after the repaired `pass42` `A1-only` and repaired `pass44` `A3-only` event-subset runs landed on the same `0.750 / 0.500 / 1.000` subject-level headline, what one bounded evaluation/reporting upgrade most improves the honesty of the current cross-family surface?

## Repo-grounded answer

The next best honesty upgrade is no longer another scalar interval field. Exact binomial confidence intervals remain necessary and should stay, but they are now identical across `pass42` and `pass44` because both runs are `1/2` on bruxism subjects and `3/3` on controls. The sharper unresolved question is paired subject instability across matched repaired family surfaces. So the next bounded reporting upgrade should be a paired subject-surface audit on the repaired `A1-only` versus repaired `A3-only` runs. [[bruxism-cap]] [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]] [[bruxism-cap-pass44-repaired-a3-event-subset-rebuild-2026-05-05]]

## Why this changed the answer

### 1. The CI patch was right, but it is no longer the discriminating next step
The repo was right to add exact/Wilson subject-level intervals, raw denominator counts, and a subject-level Brier score to `train_baseline.py`. But once `pass42` and `pass44` share the same `1/2` sensitivity and `3/3` specificity, those interval fields no longer separate the repaired family surfaces.

### 2. The repaired scaffold exposed a stronger honesty question
The new paired audit shows that the matched repaired family runs preserve the same top-line subject counts while swapping which bruxism subject is rescued:
- `brux1`: `0.136 -> 0.532` from repaired `A1-only` to repaired `A3-only`
- `brux2`: `0.825 -> 0.123`
- best-bruxism-minus-highest-control margin shrinks from `+0.339` to `+0.138`

So the benchmark is still scaffold-repaired but subject-unstable across family choice.

### 3. This upgrade stays bounded
A paired audit uses existing LOSO reports and the existing comparison helper. It does not require new training, nested CV, calibration machinery, or model-family change.

## What remains justified at `N=5`
- keep grouped `LOSO` subject-level evaluation primary
- keep random-window CV only as a leakage-reference surface
- preserve raw subject denominators and exact small-sample intervals
- keep one fixed primary subject threshold and label threshold sweeps exploratory only
- preserve one lightweight probability summary such as subject-level Brier score
- add paired matched-surface audits when two runs share the same subjects and per-subject window counts

## What remains overkill at `N=5`
- nested CV
- Platt / isotonic calibration
- threshold tuning presented as validated
- formal superiority claims between repaired family surfaces
- broader leaderboard-style benchmarking that hides subject-level instability

## One smallest repo-compatible measurement upgrade
Preserve a standard repaired-family paired surface artifact with:
- per-subject mean positive probability deltas
- prediction flips
- best-bruxism-minus-highest-control margin change
- the existing subject-level CI/Brier summaries from each underlying LOSO report

## Exact files
- Detailed report: `projects/bruxism-cap/reports/methodology-review-pass42-pass44-cross-family-upgrade-2026-05-05.md`
- Paired audit: `projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.md`
- Paired audit JSON: `projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.json`
