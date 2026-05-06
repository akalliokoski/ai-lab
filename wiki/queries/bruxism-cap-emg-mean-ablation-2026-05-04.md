---
title: Bruxism CAP EMG mean ablation (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md
  - ../projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md
---

# Question
On the strongest current EMG-first selection-aware scaffold, does removing raw `mean` rescue the remaining score-ordering problem?

# Short answer
No. It makes the strongest current EMG-first result worse.

# What was held fixed
- same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- same matched `14`-windows-per-subject` cap
- same `EMG1-EMG2` channel
- same exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- same pass18 feature table with the compact envelope / burst family
- same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`

# One change tested
Also exclude raw `mean` at train time.

# Evidence
## Window-level LOSO
- pass19 `logreg`: balanced accuracy `0.629`, sensitivity `0.043`, specificity `0.586`
- pass20 `logreg`: balanced accuracy `0.571`, sensitivity `0.000`, specificity `0.571`
- pass20 best model overall (`svm`) still reaches only balanced accuracy `0.600` with sensitivity `0.000`

## Subject-level LOSO
- pass19: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- pass20: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`

So the honest subject-level verdict does not improve at all.

## Subject score ordering (`logreg`)
- pass19: `n3` `0.280`, `n5` `0.222`, `brux1` `0.151`, `n11` `0.147`, `brux2` `0.088`
- pass20: `n3` `0.280`, `n5` `0.223`, `n11` `0.150`, `brux2` `0.083`, `brux1` `0.018`

The important shift is not at the controls. `n3` and `n5` barely move. The main change is that `brux1` collapses.

# Interpretation
The earlier audits were right that `mean` looked suspicious, but on the pass19 scaffold it was not safe to remove naively. Once the older spectral / ratio family is already gone, direct `mean` exclusion appears to remove something the model is using to keep `brux1` from collapsing entirely.

So the next lesson is narrower:
- do not keep doing deletion-only feature tweaks
- preserve pass19 as the stronger current EMG-first working point
- if `mean` is revisited, do it through robust centering / normalization-aware extraction rather than simple exclusion

# Best next bounded step
Run one compact audit on the retained pass19/pass20 feature family that compares `brux1` against `n3` and `n5` for:
- `rectified_mean`
- `rectified_std`
- `envelope_mean`
- `envelope_std`
- `p95_abs`
- `sample_entropy`

That would test whether the unresolved failure is really amplitude-scaling / envelope-shape mismatch rather than one more removable scalar feature.
