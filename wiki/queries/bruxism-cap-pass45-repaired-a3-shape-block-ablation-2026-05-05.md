---
title: Bruxism CAP pass45 repaired A3 shape-block ablation
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md
  - ../projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md
  - ../projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json
  - ../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md
  - bruxism-cap-pass45-next-step-synthesis-2026-05-05.md
---

# Bruxism CAP pass45 repaired A3 shape-block ablation

Question: on the repaired `A3-only` cross-family scaffold, does the smallest same-table shape-only ablation — dropping only `skewness`, `kurtosis`, `hjorth_mobility`, and `hjorth_complexity` while keeping the fixed pass44 event trio and LOSO contract unchanged — rescue `brux2` enough to justify preserving a new repaired `A3` working point? [[bruxism-cap]] [[bruxism-cap-pass45-next-step-synthesis-2026-05-05]] [[bruxism-cap-pass44-repaired-a3-event-subset-rebuild-2026-05-05]]

## Answer in one sentence
The no-shape ablation is directionally useful and should be preserved as the new repaired `A3` working point: it keeps the honest subject-level headline at `0.750 / 0.500 / 1.000`, improves the paired pass44 margin from `+0.138` to `+0.295`, lifts both `brux1` and `brux2`, and does not push any control above threshold.

## Why this was the smallest valid test
This run reused the frozen pass44 repaired `A3-only` feature table directly, kept the same five-subject benchmark, `EMG1-EMG2` channel, fixed 3-feature event trio, train-time exclusions, threshold `0.5`, and `logreg` LOSO contract, and changed only one thing: train-time exclusion of the four compact shape features. That means the result isolates whether secondary shape support on the repaired table was suppressing `brux2`, without reopening selector, family, channel, event-subset, or model questions. ^[../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md]

## Outcome versus pass44 and pass42
Headline subject metrics stay unchanged versus both repaired anchors:
- pass42 repaired `A1-only`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass44 repaired `A3-only`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass45 repaired `A3-only` no-shape: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000` ^[../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md]

What changed is the subject surface:
- `brux1`: `0.532 -> 0.641` versus pass44 (`+0.109`)
- `brux2`: `0.123 -> 0.178` versus pass44 (`+0.055`)
- `n11`: `0.395 -> 0.345` versus pass44 (`-0.049`)
- best-bruxism-minus-highest-control margin: `+0.138 -> +0.295` versus pass44
- no control crossed threshold, and there were no subject prediction flips versus pass44 because `brux2` still stays below threshold ^[../projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md]

Compared with repaired pass42, pass45 still does not recover the lost `brux2` rescue (`0.825 -> 0.178`), but it now strongly improves the repaired `A3-only` local surface and narrows the control gap honestly enough to preserve as the new A3 anchor. ^[../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md]

## What the paired audit adds
The new paired subject-surface artifact made the meaningful change visible even though the tiny-N headline counts stayed the same:
- paired subject rows preserved the exact per-subject score deltas
- prediction flips were copied through explicitly (`[]` versus pass44)
- best-bruxism-minus-highest-control margin change was made first-class (`+0.158` primary minus anchor)
- exact subject-level CI blocks and subject Brier summaries were copied through from both reports, showing the same `1/2` and `3/3` denominator logic but improved calibration-like surface on pass45 (`0.211` Brier versus `0.256` on pass44) ^[../projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md]

## Interpretation
This does not solve the benchmark. `brux2` still remains below threshold, so subject-level sensitivity is still only `0.500`, and future privacy / LLM-RL branches remain gated. But the result does close the exact shape-only test cleanly: compact shape-family removal on the repaired `A3-only` table helps rather than hurts, improves both bruxism subjects, lowers the highest control, and sharpens the repaired A3 margin materially without cheating on counts or selection. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

## Safest next step
Preserve pass45 no-shape as the new repaired `A3-only` anchor, then run the already-scoped backup branch: add only `evt_bursts_per_episode_mean` on top of the frozen pass42/pass45 trio while keeping the repaired scaffold, subject set, and LOSO contract fixed. [[bruxism-cap-pass45-next-step-synthesis-2026-05-05]]

## Artifacts
- Repo report: `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md`
- Paired audit: `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json`
