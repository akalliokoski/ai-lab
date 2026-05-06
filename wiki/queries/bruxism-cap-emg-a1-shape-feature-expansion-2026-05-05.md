---
title: Bruxism CAP EMG A1 shape-feature expansion (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass35-shape-feature-expansion.md
  - queries/bruxism-cap-emg-a1-record-relative-audit-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
On the repaired `SLEEP-S2 + MCAP-A1-only` percentile-band EMG scaffold, does adding one compact shape-only family (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) beat the current honest anchor or the pass34 mixed representation result?

# Short answer
Not yet. Pass35 cleanly rebuilds the exact pass27/pass28 extraction scaffold and improves the repaired EMG score ordering in a useful mixed way, but it still leaves both bruxism subjects below the subject-level threshold.

Relative to pass28, pass35 improves subject-level balanced accuracy from `0.333` to `0.500`, removes the `n3` false positive (`0.530` -> `0.225`), flips `brux2 - n3` from `-0.494` to `+0.174`, and nearly closes `n3 - brux1` from `+0.260` to `+0.009`. But `brux1` only reaches `0.216` and `brux2` only `0.399`, so subject-level sensitivity still stays `0.000`. A later honest-anchor check also shows that this is not enough to materially beat pass34 or the stronger matched `C4-P4` comparator. [[bruxism-cap]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]

# What changed
This was the bounded shape-only backup branch from the pass34 synthesis:
- rebuild the full exclusive `A1-only` EMG pool from raw EDF windows using the same `SLEEP-S2 + MCAP-A1` and `exclude MCAP-A2/A3` rule
- reapply the same percentile-band selector as pass28 (`0.10` to `0.90`, `10` windows per subject)
- keep the same `^bp_`, `^rel_bp_`, and `^ratio_` train-time exclusions
- add only four new descriptors to the retained feature table:
  - `skewness`
  - `kurtosis`
  - `hjorth_mobility`
  - `hjorth_complexity`

# Scaffold verification
The rebuilt scaffold stayed reproducible rather than drifting silently:
- full uncapped counts exactly matched pass27: `brux1 27`, `brux2 29`, `n3 29`, `n5 134`, `n11 14`
- selected percentile-band counts exactly matched pass28: `10` windows per subject, `50` rows total
- selected row metadata matched the pass28 anchor exactly, so the run remains a feature-table comparison rather than a selection change.^[../projects/bruxism-cap/reports/pass35-shape-feature-expansion.md]

# Key evidence
## Subject-level benchmark
- balanced accuracy: `0.333` -> `0.500`
- sensitivity: `0.000` -> `0.000`
- specificity: `0.667` -> `1.000`
- best-bruxism-minus-highest-control margin: `-0.260` -> `+0.012`

## Subject score shifts
- `brux1`: `0.270` -> `0.216`
- `brux2`: `0.036` -> `0.399`
- `n3`: `0.530` -> `0.225`
- `n5`: `0.291` -> `0.387`
- `n11`: `0.325` -> `0.188`

## Gap-focused checks
- `n3 - brux1`: `+0.260` -> `+0.009`
- `brux2 - n3`: `-0.494` -> `+0.174`

The added shape family therefore improves both named EMG failure gaps more symmetrically than pass34, but the gains still stop short of an honest positive subject verdict.^[../projects/bruxism-cap/reports/pass35-shape-feature-expansion.md]

# Verdict
Preserve pass35 as a second mixed representation result, not a new honest win. It is stronger than a negative ablation because it repairs both the `n3` false positive and the `brux2` reversal while leaving the scaffold unchanged, but it still fails the decision criterion that matters: at the subject level, neither `brux1` nor `brux2` crosses threshold. The later honest-anchor comparison should therefore be treated as the governing interpretation: pass35 is directionally better than the older EMG anchors, but it does not materially beat pass34 or pass29 overall. [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]

# Best next bounded step
Do not silently overwrite pass34 with pass35, but do not spend another cycle only choosing between them either. Preserve that pass34 is the stronger pure within-record normalization result for `brux2` while pass35 is the stronger shape-family result for shrinking both named score gaps, then test whether those two gains compose honestly on one scaffold. The next bounded step should add the same four compact shape features on top of the pass34 record-relative scaffold and run a strict pass34 versus `record-relative + shape` LOSO comparison on the same five-subject split. [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]
