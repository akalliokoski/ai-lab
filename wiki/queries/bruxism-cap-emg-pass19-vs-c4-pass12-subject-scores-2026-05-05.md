---
title: Bruxism CAP pass19 EMG vs pass12 C4 subject-score comparison (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [experiment, evaluation, dataset, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md
  - ../projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md
  - ../projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md
  - ../projects/bruxism-cap/reports/subject-score-comparison-pass23-emg-pass19-vs-c4-pass12.json
---

# Question
What does a direct shared subject-score comparison show between the strongest current EMG-first working point (`pass19 EMG1-EMG2 A3-only` with selection-aware train-time exclusions) and the strongest current honest comparison anchor (`pass12 C4-P4 A1-only`)?

# Short answer
The comparison keeps the EMG-first direction intact but preserves a sharper negative result: `pass19` does improve `brux1` relative to the `pass12` anchor, yet it still loses decisively overall because `brux2` collapses under EMG and `n3` becomes the highest-score control.

So the remaining EMG gap is now more specific than “EMG is worse.” It is:
- one bruxism subject that gets somewhat better (`brux1`)
- one bruxism subject that gets much worse (`brux2`)
- one control subject that becomes the main blocker (`n3`)

That makes the next bounded experiment clearer: audit `brux2` versus `n3` on the fixed pass19 scaffold rather than doing another broad extraction rewrite. [[bruxism-cap]] [[bruxism-cap-emg-median-mad-normalization-2026-05-04]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

# Shared subject table

| Subject | Label | pass19 EMG score | pass12 C4 score | Delta (EMG-C4) |
|---|---|---:|---:|---:|
| brux1 | bruxism | 0.151 | 0.018 | +0.134 |
| brux2 | bruxism | 0.088 | 0.795 | -0.708 |
| n11 | control | 0.147 | 0.273 | -0.126 |
| n3 | control | 0.280 | 0.245 | +0.036 |
| n5 | control | 0.222 | 0.433 | -0.212 |

# Core evidence

## Honest margin comparison
- pass19 best bruxism minus highest control: `-0.129`
- pass12 best bruxism minus highest control: `+0.362`
- margin swing from pass12 to pass19: `-0.491`

That single margin comparison explains why the honest baseline still belongs to the pass12 anchor.

## What improved under EMG
- `brux1` rises from `0.018` on pass12 to `0.151` on pass19.
- `n5` falls from `0.433` on pass12 to `0.222` on pass19.

So the EMG surface is not uniformly worse. It changes the failure shape.

## What regressed under EMG
- `brux2` collapses from `0.795` to `0.088`.
- the highest-score control switches from `n5` on pass12 to `n3` on pass19.
- pass19 subject-level sensitivity stays `0.000`, while pass12 reaches `0.500`.

That is the main reason the EMG-first working point remains a useful negative comparator rather than the best honest baseline.

# Updated interpretation
- Keep `EMG1-EMG2` as the primary next-pass channel. The comparison does **not** justify reverting to EEG-first framing.
- Keep pass19 as the current EMG working point because pass22 already showed that another immediate normalization rewrite made things worse.
- Treat pass12 `C4-P4 A1-only` as the honest benchmark anchor that EMG still needs to beat.
- Narrow the next EMG-first question to subject-specific validity: why does `brux2` collapse under EMG while `n3` remains the top control?

# Best next bounded experiment
Keep the pass19 scaffold fixed and run one compact audit focused on:
1. `brux2` versus `n3` subject summaries on the saved pass19 folds
2. whether one small extraction or feature-behavior difference explains the `brux2` collapse
3. whether that difference can be tested without changing the verified subject subset, overlap rule, or train-time feature-selection contract
