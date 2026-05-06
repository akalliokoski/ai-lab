---
title: Bruxism CAP C4 record-relative comparator (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass35-record-relative-c4-comparator.md
  - queries/bruxism-cap-emg-a1-record-relative-audit-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
If the pass34 within-record robust feature-space transform is rebuilt on the same repaired `C4-P4 A1-only` percentile-band scaffold, does it preserve or erase the earlier matched channel advantage over `EMG1-EMG2`?

# Short answer
It erases most of that advantage and changes the failure mode. The same record-relative transform that helped the repaired EMG scaffold does not transfer cleanly to `C4-P4`: subject-level balanced accuracy drops from `0.750` to `0.583`, `brux2` collapses below `n3`, and `n3` becomes a new false positive.

At the same time, this is still a useful comparator result rather than just a regression. The transform is now confirmed to be scaffold-matched across channels, so the repo can say something sharper: the pass34 gain was not a universal cleanup of the repaired benchmark. It appears more specifically aligned with the EMG failure surface, because on `C4-P4` it trades away the old `brux2` recovery while boosting `brux1` instead. [[bruxism-cap]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]]

# What stayed matched
- same repaired `SLEEP-S2 + MCAP-A1-only` percentile-band subset
- same timing-selector columns and row identities across transformed `EMG1-EMG2` and `C4-P4`
- same retained trainable feature list
- same relative-feature transform list
- same `^bp_`, `^rel_bp_`, and `^ratio_` train-time exclusions
- same `logreg` LOSO evaluation contract

The only intentional divergence was the baseline channel source: pass34 started from the pass28 `EMG1-EMG2` table, while this comparator starts from the pass29 `C4-P4` table.

# Key evidence
## Inside-channel `C4-P4` change
- balanced accuracy: `0.750` -> `0.583`
- sensitivity: `0.500` -> `0.500`
- specificity: `1.000` -> `0.667`
- best-bruxism-minus-highest-control margin: `+0.542` -> `+0.069`

## Subject score shifts
- `brux1`: `0.405` -> `0.669`
- `brux2`: `0.959` -> `0.262`
- `n3`: `0.417` -> `0.600`
- `n5`: `0.212` -> `0.325`
- `n11`: `0.188` -> `0.295`

## Failure-surface swap
- `n3 - brux1`: `+0.012` -> `-0.069`
- `brux2 - n3`: `+0.542` -> `-0.338`

So the transform does not just “shrink scores” or “smooth both channels” in a simple way. On `C4-P4`, it flips which bruxism subject is recoverable: `brux1` rises above threshold, but the earlier strong `brux2` separator is lost and `n3` crosses above threshold instead.^[../projects/bruxism-cap/reports/pass35-record-relative-c4-comparator.md]

## Matched transformed channel comparison
- pass34 EMG relative balanced accuracy: `0.500`
- pass35 C4 relative balanced accuracy: `0.583`
- pass34 EMG relative best-bruxism-minus-highest-control margin: `+0.041`
- pass35 C4 relative best-bruxism-minus-highest-control margin: `+0.069`
- pass34 EMG relative `brux2 - n3`: `+0.041`
- pass35 C4 relative `brux2 - n3`: `-0.338`

This means `C4-P4` is still slightly ahead on the transformed scaffold by the coarse balanced-accuracy summary, but the original clean comparator story is gone. The relative transform largely destroys the old `C4` advantage and makes the benchmark much less cleanly channel-separated.

# Verdict
Preserve pass35 as a matched comparator and as evidence against over-generalizing pass34. The within-record robust feature-space normalization is not a universal scaffold improvement. It helped the EMG failure surface, but on `C4-P4` it weakens the strongest prior separator (`brux2 > n3`) and introduces a new `n3` false positive.

# Best next bounded step
Do not make record-relative normalization the new default cross-channel scaffold. Treat pass34/pass35 together as a representation-localization result: the transform is worth preserving as an EMG-specific clue, not as a channel-agnostic fix. The next bounded experiment should still be the compact EMG shape-family backup (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) on the repaired EMG scaffold without stacking another normalization change.
