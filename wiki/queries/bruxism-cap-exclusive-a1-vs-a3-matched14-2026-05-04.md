---
title: Bruxism CAP exclusive A1 vs A3 matched-family comparison 2026-05-04
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [dataset, evaluation, experiment, research, notes]
sources:
  - ../projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md
  - ../projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json
  - ../projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json
  - ../projects/bruxism-cap/reports/pass11-rule-survival-audit.md
---

# Bruxism CAP exclusive A1 vs A3 matched-family comparison 2026-05-04

A new bounded comparison tested the next validity question suggested by [[bruxism-cap]] and [[bruxism-cap-rule-survival-audit-2026-05-04]]: compare exclusive `SLEEP-S2 + MCAP-A1-only` against exclusive `SLEEP-S2 + MCAP-A3-only` on the same verified 5-subject CAP subset with the same per-subject cap. [[bruxism-cap-first-baseline-lessons-2026-05-03]] [[bruxism-cap-annotation-alignment-audit-2026-05-03]]

## Setup
- Subjects stayed fixed at `brux1`, `brux2`, `n3`, `n5`, `n11`.
- The cap was reduced to `14` windows per subject because `n11` had only `14` eligible `A1-only` windows locally, while all subjects had at least `14` eligible `A3-only` windows.
- Model family stayed fixed: the existing logistic regression, SVM, and random forest baselines from the current repo path.

## Main result
- Matched `A1-only` improved honest transfer over matched `A3-only`.
- Best `A1-only` LOSO window-level balanced accuracy reached `0.686` with logistic regression, versus `0.514` for matched `A3-only`.
- Best `A1-only` subject-level LOSO summary reached balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`.
- Matched `A3-only` still showed `0.000` subject-level bruxism sensitivity for every tested model.

## Why this matters
This is the first overlap-family comparison in the project that changes the honest interpretation surface without changing model class. It suggests that the previous focus on exclusive `A3` windows was too narrow: under matched conditions, `A1-only` is the stronger transfer candidate in this tiny subset. But the result is still fragile rather than decisive, because the improvement comes from recognizing `brux2` while `brux1` still fails.

## Negative result preserved
The comparison is not a claim that the project now has a trustworthy detector:
- random-window CV stayed high for both families, so random splits remain misleading
- `A1-only` still missed one of the two held-out bruxism subjects at the subject level
- the result depends on a tiny `5`-subject matched subset and should be treated as a measurement clue, not a stable baseline

## Best next step
The next bounded validity increment should stay on the pass12 surface and audit subject-level score margins for `brux1` versus `brux2`. The key question is whether the `A1-only` gain reflects a broad ranking improvement or only a threshold-sensitive win on one subject. [[bruxism-cap]] [[bruxism-cap-rule-survival-audit-2026-05-04]]
