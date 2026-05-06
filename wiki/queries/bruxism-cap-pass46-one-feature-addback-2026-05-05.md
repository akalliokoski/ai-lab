---
title: Bruxism CAP pass46 one-feature evt_bursts_per_episode_mean add-back
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md
  - ../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md
  - ../projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json
  - bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05.md
  - bruxism-cap-campaign-handoff-2026-05-05.md
---

# Bruxism CAP pass46 one-feature `evt_bursts_per_episode_mean` add-back

Question: after `pass45` became the repaired `A3-only` no-shape anchor, does restoring only `evt_bursts_per_episode_mean` on top of the frozen pass42/pass45 scaffold improve the unresolved `brux2` miss enough to justify promoting a new repaired `A3` anchor? [[bruxism-cap]] [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

## Answer in one sentence
Only directionally: `pass46` improves `brux2` slightly relative to `pass45` and keeps controls closed, but it does not beat the frozen `pass45` repaired `A3-only` anchor on the overall paired margin, so the honest durable read stays "interesting variant, not yet promoted replacement." 

## What stayed fixed
This was a real one-feature add-back rather than a hidden scaffold rewrite:
- same repaired `A3-only` selected rows (`50`, `10` per subject)
- same `EMG1-EMG2` channel
- same `logreg` LOSO contract and threshold `0.5`
- same pass45 shape-drop exclusions (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`)
- same validated pass42 event trio (`evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`)
- only one new restored feature: `evt_bursts_per_episode_mean` ^[../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md]

## Outcome versus pass45 and pass42
The tiny-N headline does not change:
- pass42: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass45: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass46: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity ^[../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md]

The repaired `A3-only` subject surface changes only a little:
- `brux1`: `0.641 -> 0.639` versus pass45 (`-0.002`)
- `brux2`: `0.178 -> 0.196` versus pass45 (`+0.018`)
- `n5`: `0.337 -> 0.347` versus pass45 (`+0.010`)
- `n11`: `0.345 -> 0.345` versus pass45 (`~0.000`)
- no subject prediction flips occur versus pass45 ^[../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md]

## Did `brux2` improve relative to the highest control?
Yes, but only slightly.

Using each run's own highest control:
- pass42 `brux2 - highest_control`: `+0.339`
- pass45 `brux2 - highest_control`: `-0.167`
- pass46 `brux2 - highest_control`: `-0.151` ^[../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md]

So the add-back does narrow the `brux2` gap on repaired `A3-only`, but it still leaves `brux2` below the highest control and far behind repaired `pass42`.

## Why pass45 still stays the cleaner repaired A3 anchor for now
The paired audit is the decisive tie-breaker:
- pass45 best-bruxism-minus-highest-control margin: `+0.295`
- pass46 best-bruxism-minus-highest-control margin: `+0.292`
- paired margin delta (`pass46 - pass45`): `-0.004` ^[../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md]

That means the one-feature add-back helps the specific `brux2` question a little, but the total repaired `A3-only` surface does not improve cleanly enough to replace `pass45` outright.

## Durable interpretation
`evt_bursts_per_episode_mean` is still not noise: adding it back on the frozen repaired scaffold produces a consistent small `brux2` lift without reopening false positives. But the effect is weaker than the preserved pass45 no-shape gain and not strong enough to change the benchmark verdict from `ambiguous`. `brux2` remains below threshold and below the highest control, while repaired `A1-only` pass42 still keeps the much stronger `brux2` rescue. [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]]

## Safest next bounded step
Do one interpretation-preservation pass, not another immediate feature rerun: compare `pass45` and `pass46` directly against repaired `pass42` and decide whether the tiny `brux2` improvement is large enough to preserve `pass46` as the new repaired `A3-only` anchor or whether `pass45` should remain the durable anchor. That keeps the branch honest without reopening scaffold, family, privacy, or LLM/RL scope.

## Artifacts
- Repo report: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md`
- Paired audit: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json`
