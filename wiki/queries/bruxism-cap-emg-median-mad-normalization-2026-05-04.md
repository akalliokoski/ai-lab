---
title: Bruxism CAP EMG median-MAD normalization rerun (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, notes, research]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md
  - ../projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json
  - ../projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json
  - ../projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json
---

# Question
Did one normalization-aware EMG extraction change improve the current pass19 `EMG1-EMG2` working point on the matched CAP subset?

# Short answer
No. Robust per-window `median_mad` normalization made the EMG-first result worse.

## What was held fixed
- same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- same exclusive `SLEEP-S2 + MCAP-A3-only` rule
- same `14` windows per subject
- same train-time exclusions as pass19: `^bp_`, `^rel_bp_`, `^ratio_`
- same simple baseline models and LOSO evaluation

## What changed
Only the extraction path changed:
- each 30 s EMG window was robust-centered and scaled before feature computation using `median(signal)` and `1.4826 * MAD(signal)` with `std` fallback
- the resulting feature table is `window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`

## Main result
The stronger EMG-first working point remains pass19.

### LOSO window-level comparison
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 `EMG1-EMG2 A3-only` + envelope family + spectral/ratio exclusions | `logreg` | `0.629` | `0.043` | `0.586` |
| pass22 same scaffold + `median_mad` extraction | `svm` | `0.571` | `0.000` | `0.571` |

### LOSO subject-level comparison
| Run | Best subject-level balanced accuracy | Sensitivity | Specificity |
|---|---:|---:|---:|
| pass19 | `0.500` | `0.000` | `1.000` |
| pass22 | `0.500` | `0.000` | `1.000` |

So the normalization-aware rerun did not move the honest subject verdict at all, and it regressed the best window-level LOSO result.

## Subject ordering got worse, not better
On the pass19 `logreg` working point, the ranking was:
- `n3` `0.280`
- `n5` `0.222`
- `brux1` `0.151`
- `n11` `0.147`
- `brux2` `0.088`

On the pass22 `logreg` rerun, it became:
- `n11` `0.270`
- `n5` `0.251`
- `n3` `0.195`
- `brux2` `0.033`
- `brux1` `0.009`

That is a stronger negative result than pass20 in one important sense: the normalization change pushed **both** bruxism subjects farther down the ranking, not just `brux1`.

## What this means
The pass21 suspicion was reasonable: maybe the retained envelope family needed normalization-aware extraction rather than more deletion. But the direct test says that simple per-window robust normalization is not the fix on this scaffold.

The practical lesson is narrower:
- the retained pass19 family may still contain some useful amplitude information
- normalizing every window before feature extraction appears to erase or distort too much of that weak signal
- the next best move is not another extraction rewrite by default

## Baseline verdict
This latest EMG rerun does **not** beat either:
- the current EMG working point: pass19 `EMG1-EMG2 A3-only`
- the current best honest baseline: pass12 `C4-P4 A1-only`, which still has subject-level balanced accuracy `0.750` and subject sensitivity `0.500`

## Best next bounded experiment
Build one shared subject-score comparison between:
- pass19 `EMG1-EMG2 A3-only`
- pass12 `C4-P4 A1-only`

That should clarify whether the remaining failure is mainly about channel family, overlap family, or one specific subject (`brux1`) instead of launching another extraction rewrite immediately.
