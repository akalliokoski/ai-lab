---
title: Bruxism CAP EMG1-EMG2 A1-only vs A3-only on matched subset (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md
  - ../projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md
---

# Question
On the same verified `5`-subject CAP subset and same `14`-windows-per-subject cap, does `EMG1-EMG2` transfer better with exclusive `SLEEP-S2 + MCAP-A1-only` or exclusive `SLEEP-S2 + MCAP-A3-only`?

# Short answer
`A3-only` is the better EMG family on the current matched scaffold, but it is still not an honest baseline win.

Compared with the earlier EMG `A1-only` rerun, `EMG1-EMG2` `A3-only` improved window-level LOSO balanced accuracy from `0.543` to `0.629` and reduced several control-subject mean scores. But subject-level bruxism sensitivity stayed `0.000`, so neither EMG family currently recognizes a held-out bruxism subject at the default threshold. [[bruxism-cap]] [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]]

# What was held constant
- subject set: `brux1`, `brux2`, `n3`, `n5`, `n11`
- windows per subject: `14`
- channel: `EMG1-EMG2`
- model family: `logreg`, `svm`, `random_forest`
- training path: current no-`n_samples` / no-`duration_s` feature exclusion in `train_baseline.py`

# Result summary

## Window-level LOSO
- `A1-only` best: balanced accuracy `0.543`, sensitivity `0.043`, specificity `0.500`
- `A3-only` best: balanced accuracy `0.629`, sensitivity `0.057`, specificity `0.571`

## Subject-level LOSO
- `A1-only` best: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- `A3-only` best: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`

# Updated interpretation
- The earlier pass13 lesson was too narrow to stop at “EMG failed on `A1-only`.” The family choice matters inside EMG too.
- But the newer pass14 lesson is still negative on the honest criterion: even the better EMG family has not yet produced a positive held-out bruxism subject.
- The project should therefore stay EMG-first, but move to score/threshold auditing before any model-complexity change. [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]] [[bruxism-better-project-and-data-options-2026-05-04]]

# Best next bounded experiment
Run a compact threshold audit on the strongest current EMG LOSO model (`A3-only` `logreg`):
- inspect subject mean-score margins for `brux1` and `brux2`
- test whether a lower subject threshold improves sensitivity without immediately breaking control specificity
- keep pass12 `C4-P4 A1-only` as the fixed honest baseline anchor
