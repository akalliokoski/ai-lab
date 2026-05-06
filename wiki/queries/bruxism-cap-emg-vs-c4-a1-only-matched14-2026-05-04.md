---
title: Bruxism CAP EMG1-EMG2 vs C4-P4 on matched A1-only subset (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md
  - ../projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md
---

# Question
On the same verified `5`-subject CAP subset and same exclusive `SLEEP-S2 + MCAP-A1-only` rule, does switching from `C4-P4` to `EMG1-EMG2` improve the current honest baseline?

# Short answer
No. The first matched EMG rerun regressed the current honest baseline.

`EMG1-EMG2` stayed plausible under random-window CV, but it did not beat the existing `C4-P4` matched `A1-only` baseline on LOSO. The current best `C4-P4` run still recognizes `brux2` at the subject level, while the new `EMG1-EMG2` run recognizes neither held-out bruxism subject.

# What was held constant
- subject set: `brux1`, `brux2`, `n3`, `n5`, `n11`
- windows per subject: `14`
- extraction rule: in-range `SLEEP-S2` windows overlapping `MCAP-A1` and excluding simultaneous `MCAP-A2` / `MCAP-A3`
- model family: `logreg`, `svm`, `random_forest`
- training path: current no-`n_samples` / no-`duration_s` feature exclusion in `train_baseline.py`

# Result summary

## Window-level LOSO
- `C4-P4` best: balanced accuracy `0.686`, sensitivity `0.186`, specificity `0.500`
- `EMG1-EMG2` best: balanced accuracy `0.543`, sensitivity `0.043`, specificity `0.500`

## Subject-level LOSO
- `C4-P4` best: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `EMG1-EMG2` best: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`

# Why this matters
This is a useful negative result, not a dead end. It shows that the EMG-first framing is still scientifically motivated, but the current reusable feature recipe plus the current strongest `A1-only` subset do not automatically transfer better just because the signal channel is more jaw-muscle-aligned. [[bruxism-cap]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

# Updated interpretation
- The earlier pass12 lesson still stands for the current scaffold: exclusive `A1-only` is stronger than matched exclusive `A3-only` for `C4-P4`.
- The new pass13 lesson is narrower: that same `A1-only` rule is **not yet** a stronger cross-subject baseline when the channel is switched to `EMG1-EMG2`.
- So the next EMG-first pass should compare **EMG family preference**, not assume the best `C4-P4` family transfers unchanged to EMG.

# Best next bounded experiment
Run a matched `EMG1-EMG2` family comparison on the same verified subset:
- exclusive `A1-only` vs exclusive `A3-only`
- same `14` windows per subject
- same LOSO + subject-level evaluation

That is the tightest next step for deciding whether the EMG regression is channel-wide or whether EMG simply prefers a different overlap family than the current `C4-P4` anchor.
