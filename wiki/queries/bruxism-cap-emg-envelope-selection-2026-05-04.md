---
title: EMG envelope family under stricter feature selection (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md
  - ../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md
---

# Question
Does the pass18 EMG envelope / burst family become more useful if the older spectral / ratio family is excluded at train time on the same matched `EMG1-EMG2 A3-only` scaffold?

# Short answer
A little, but not enough.

The stricter train-time filter is directionally better than pass18 add-only expansion:
- it recovers the best pass14 LOSO balanced accuracy (`0.629`)
- it improves LOSO specificity relative to pass14 (`0.571` -> `0.586`)
- it keeps `n5` below its pass18 score and below `n3`

But it still does **not** change the honest subject-level verdict:
- subject-level sensitivity stays `0.000`
- both `n3` and `n5` still outrank `brux1`
- `brux2` remains too low to matter at the subject threshold

[[bruxism-cap]] [[bruxism-cap-emg-envelope-replacement-2026-05-04]] [[bruxism-cap-emg-feature-validity-audit-2026-05-04]]

# What was held constant
- verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- rule: exclusive `SLEEP-S2 + MCAP-A3-only`
- cap: `14` windows per subject
- feature table: pass18 envelope / burst CSV
- model family: unchanged `logreg` / `svm` / `random_forest`

Only the train-time feature set changed:
- kept the time-domain core plus the pass18 EMG envelope / burst family
- excluded `bp_*`, `rel_bp_*`, and `ratio_*`

# Key evidence

## Window-level LOSO summary
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` | `0.629` | `0.057` | `0.571` |
| pass17 time-only | `logreg` | `0.614` | `0.043` | `0.571` |
| pass18 envelope add-on | `logreg` | `0.600` | `0.043` | `0.557` |
| pass19 envelope + strict selection | `logreg` | `0.629` | `0.043` | `0.586` |

This is a real but narrow gain: stricter selection helps the pass18 EMG family more than add-only expansion did, but it does not beat the best honest window-level balanced accuracy already seen in pass14.^[concepts/bruxism-cap.md]

## Subject-level result still fails
All pass19 models still stay at:
- subject balanced accuracy `0.500`
- subject sensitivity `0.000`
- subject specificity `1.000`

So this pass is still a validity note, not a baseline win.^[../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md]

## Score ordering stayed wrong
Pass19 `logreg` subject means:
- `n3` `0.280`
- `n5` `0.222`
- `brux1` `0.151`
- `n11` `0.147`
- `brux2` `0.088`

Relative to pass18, this is mixed but directionally informative:
- `n5` improves materially (`0.267` -> `0.222`)
- `brux2` stays slightly better than pass14 (`0.088` vs `0.074`)
- `brux1` does not recover enough (`0.151` vs `0.176` in pass14)
- `n3` is still too high (`0.280`)

So the pass18 EMG family is more useful when the older spectral / ratio family is removed, but the remaining failure is still the ordering of `n3`, `n5`, and `brux1` rather than raw threshold choice.^[../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md]

# Practical lesson
The project should stay EMG-first, but the repo evidence now supports a narrower rule:

**If the pass18 envelope / burst family is kept, it should be evaluated with stricter train-time feature selection rather than simply stacked on top of the older EEG-shaped spectral family.**

That is a better direction than pass18, but it still does not beat the current honest baseline anchor, which remains pass12 `C4-P4 A1-only` at the subject level.

# Best next bounded step
Keep the same pass19 scaffold and test one small validity move only:
1. audit or ablate `mean` on the selection-aware EMG recipe, because it remains the most suspicious large negative driver on `brux1`, or
2. produce one shared subject-score comparison table between pass12 `C4-P4 A1-only`, pass14 EMG `A3-only`, pass18, and pass19 so the remaining gap is more legible.

The safer next step is the first one: keep everything else fixed and test `mean` handling before touching model family, overlap family, or dataset scope.
