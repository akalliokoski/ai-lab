---
title: Bruxism CAP EMG envelope-family audit (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md
  - ../projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md
---

# Question
On the strongest current EMG-first selection-aware scaffold, does the retained amplitude / envelope family explain why `n3` and `n5` still outrank `brux1`?

# Short answer
Yes, partly: the retained family is active, but it is still not cleanly bruxism-aligned on this tiny matched subset.

# What was held fixed
- same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- same matched `14`-windows-per-subject cap
- same `EMG1-EMG2` channel
- same exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
- same `logreg` decision surface reconstructed from the saved pass19 context

# One change tested
Do not launch another model rerun. Instead, audit the retained pass19 family directly with `projects/bruxism-cap/src/audit_emg_envelope_family.py` and summarize how the focused retained features behave for each subject:
- `sample_entropy`
- `rectified_mean`
- `rectified_std`
- `envelope_mean`
- `envelope_std`
- `envelope_cv`
- `burst_fraction`
- `burst_rate_hz`
- `p95_abs`

# Evidence
## Subject score ordering (`logreg`)
- `n3` `0.280`
- `n5` `0.222`
- `brux1` `0.151`
- `n11` `0.147`
- `brux2` `0.088`

The audit reproduces the pass19 ranking exactly, so the failure shape is stable rather than a reporting artifact.

## What still helps the highest-score controls
- `sample_entropy` remains a positive driver for `n3` and `n5`
- `burst_fraction` also contributes positively to the control side of the ranking
- together, those terms help keep both controls above `brux1` even after the older spectral / ratio family has already been excluded

## What still hurts `brux1`
- `brux1` does look different in raw amplitude terms: `rectified_mean`, `envelope_mean`, and `p95_abs` are all much larger than on the control side
- but under the learned pass19 coefficients, those same larger amplitude-envelope values remain net-negative contributors for `brux1`
- `burst_rate_hz` does push back in `brux1`'s favor, but not strongly enough to overcome the control-favoring pieces

# Interpretation
This is a useful EMG-first validity note because it shows the retained pass19 family is not inert. The newer envelope / burst summaries are materially shaping the score surface.

But it is still not an honest EMG-first win:
- the retained family does not create a clean `brux1`-over-control ordering
- simply having larger raw amplitude-envelope values is not enough under the current standardized / learned coefficient geometry
- the remaining blocker now looks more like scaling / normalization behavior than one more obviously removable feature

That makes the next lesson narrower than pass20:
- preserve pass19 as the current EMG-first working point
- preserve pass21 as evidence that the retained family is real but misaligned
- test one normalization-aware extraction change before deleting more features or changing model family

See also [[bruxism-cap]] and [[bruxism-cap-emg-mean-ablation-2026-05-04]].

# Best next bounded step
Keep the pass19 scaffold fixed and regenerate the same matched `EMG1-EMG2 A3-only` feature table with one normalization-aware extraction change that preserves the retained family, for example:
- robust per-window centering before envelope summaries
- robust scaling of the retained amplitude features before model fit
- a bounded replacement of raw amplitude level with a normalized envelope-shape counterpart

The key rule for that next pass is to change only one normalization axis while leaving subject subset, overlap rule, and evaluation surface unchanged.
