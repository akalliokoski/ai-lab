---
title: Bruxism CAP strict time-position matched C4-vs-EMG A3 comparison (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - queries/bruxism-cap-emg-a3-time-position-matched-rerun-2026-05-05.md
---

# Question
On the stricter shared-time-position `SLEEP-S2 + MCAP-A3-only` scaffold, does switching from `EMG1-EMG2` back to `C4-P4` rescue the benchmark?

# Short answer
No.

Rebuilding the exact same shared-interval / `10`-windows-per-subject scaffold on `C4-P4` does **not** beat the matched `EMG1-EMG2` rerun on the honest LOSO surface, and it still does not recover any held-out bruxism subject. [[bruxism-cap]] [[bruxism-cap-emg-a3-time-position-matched-rerun-2026-05-05]]

# What was held fixed
- verified subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- annotation rule: in-range `SLEEP-S2` plus exclusive `MCAP-A3-only`
- shared interval: `3210.0` to `12230.0`
- per-subject cap: `10`
- train-time exclusions: `^bp_`, `^rel_bp_`, `^ratio_`

So this is a true channel comparison on one strict scaffold, not a new availability change.

# Key result

## Random-window CV still favors `C4-P4`
- strict-scaffold `EMG1-EMG2`: best random balanced accuracy `0.808`
- strict-scaffold `C4-P4`: best random balanced accuracy `0.883`

That is the same trap as earlier passes: the random split again flatters `C4-P4`, so it is not the surface to trust.

## Honest LOSO does **not** favor `C4-P4`
- strict-scaffold `EMG1-EMG2`: best LOSO balanced accuracy `0.600`, subject-level `0.500 / 0.000 / 1.000`
- strict-scaffold `C4-P4`: best LOSO balanced accuracy `0.520`, subject-level `0.333 / 0.000 / 0.667`

So under the stricter matched scaffold, `EMG1-EMG2` is actually **less bad** than `C4-P4` on the honest metric, even though both still fail the baseline criterion.

# Subject-level failure shape

## `EMG1-EMG2` pass25 best LOSO model (`svm`)
- `n11` `0.445`
- `n3` `0.442`
- `n5` `0.348`
- `brux1` `0.329`
- `brux2` `0.273`

## `C4-P4` pass26 best LOSO model (`logreg`)
- `n3` `0.535`
- `brux2` `0.464`
- `n11` `0.356`
- `n5` `0.337`
- `brux1` `0.086`

This matters because it rules out the simple fallback story that “EEG would fix the stricter scaffold.” It does not. `C4-P4` still misses both bruxism subjects and also promotes `n3` above threshold. [[bruxism-cap]]

# Interpretation
1. The pass25 negative result should **not** be read as evidence that `EMG1-EMG2` itself is unusable.
2. On the exact same strict scaffold, `C4-P4` performs worse on the honest LOSO summary.
3. The stronger hypothesis now is that the shared-time-position `A3-only` benchmark surface is itself too hostile or too poorly aligned, rather than the project simply choosing the wrong channel.
4. This preserves the EMG-first framing: the repo still has no evidence strong enough to revert to EEG-first.

# Best next bounded step
Keep the EMG-first framing and move to the stronger family under the stricter timing rule:
- rebuild the same shared-time-position scaffold on `EMG1-EMG2` exclusive `A1-only`
- use `C4-P4` only as the matched comparison channel after that EMG rerun exists

That tests whether the current failure is mostly `A3-only`-specific while preserving the new time-position discipline.
