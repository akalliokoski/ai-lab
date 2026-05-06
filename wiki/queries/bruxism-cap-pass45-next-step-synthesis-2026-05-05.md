---
title: Bruxism CAP pass45 next-step synthesis
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md
  - ../projects/bruxism-cap/reports/pass45-jaw-emg-burst-organization-literature-memo.md
  - ../projects/bruxism-cap/reports/methodology-review-pass42-pass44-cross-family-upgrade-2026-05-05.md
  - bruxism-cap-pass44-cross-family-asymmetry-audit-2026-05-05.md
  - bruxism-cap-pass42-pass44-cross-family-methodology-review-2026-05-05.md
---

# Bruxism CAP pass45 next-step synthesis

Question: after pass44 repaired the `A3-only` scaffold, the fresh jaw-EMG literature lane proposed one small cluster-density add-back, and the methodology lane proposed paired subject-surface reporting, what should the repo promote next as exactly one primary experiment and one bounded measurement upgrade? [[bruxism-cap]] [[bruxism-cap-pass44-cross-family-asymmetry-audit-2026-05-05]] [[bruxism-cap-pass42-pass44-cross-family-methodology-review-2026-05-05]]

## Answer in one sentence
Promote one repaired-`A3-only` same-table shape-only ablation as the primary experiment and one standardized paired subject-surface audit as the measurement upgrade; keep the one-feature `evt_bursts_per_episode_mean` add-back alive only as the backup branch.

## Current bottleneck after synthesis
The repaired cross-family branch is no longer blocked on transfer itself. Pass44 already showed that the fixed 3-feature event subset reaches the same honest headline on repaired `A1-only` and repaired `A3-only`. The unresolved bottleneck is narrower: the benchmark is now count-matched but subject-unstable, because repaired `A1-only` rescues `brux2` while repaired `A3-only` rescues `brux1`. ^[../projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md]

On repaired `A3-only`, the active miss is `brux2` staying low across the whole table (`0.123`) while `brux1` is rescued to `0.532`. The asymmetry audit says that split is carried primarily by the retained amplitude / dispersion block, with the compact shape block as the cleanest secondary same-table target and the retained event trio no longer looking like the main blocker by itself. ^[../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md]

## Which ideas survived repo contact
### Keep the validated event trio as the base
The literature and the repaired pass42/pass44 results now agree that `evt_active_fraction`, `evt_burst_duration_median_s`, and `evt_interburst_gap_median_s` should stay fixed as the current burst-organization base block rather than being reopened immediately. ^[../projects/bruxism-cap/reports/pass45-jaw-emg-burst-organization-literature-memo.md]

### Promote shape-only ablation first
The compact shape-family ablation survives because it is the smallest same-table test that directly targets a plausible `brux2` suppressor without reopening selector, family, channel, event-subset, or model questions. Repo contact matters here: `brux2` loses more shape support than `brux1` after the repaired family swap, while the event-block separation between them stays small. ^[../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md]

### Promote paired subject-surface audits as the next reporting standard
The methodology lane survives unchanged: exact subject-level CIs remain necessary, but they no longer distinguish repaired pass42 from repaired pass44 because the counts are identical. The more informative honesty artifact is a paired subject-surface audit that makes subject rescues, subject collapses, and margin changes explicit. ^[../projects/bruxism-cap/reports/methodology-review-pass42-pass44-cross-family-upgrade-2026-05-05.md]

## Which ideas were rejected and why
### Not promoted first: `evt_bursts_per_episode_mean` add-back
This remains literature-backed, but it loses the primary slot after repo contact because the current repaired `A3-only` split is not mainly event-separated. The pass44 `brux1` vs `brux2` event-block delta is only `-0.059`, so a one-feature add-back is less direct than first testing whether removing compact shape drag lets `brux2` rise on the frozen table. ^[../projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md]

### Rejected for now: raw event-count reopenings, another scaffold rewrite, model-family pivots, privacy promotion, and LLM/RL promotion
These all fail the current boundedness test. The literature warns against over-reading crude episode counts, pass44 already closed the scaffold-transfer question, and the benchmark is still not handoff-grade enough to justify promoting the future branches. ^[../projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md]

## Chosen experiment
Run one repaired-`A3-only` same-table shape-only ablation:
- keep the repaired pass44 rows fixed
- keep the validated 3-feature event trio fixed
- drop only `skewness`, `kurtosis`, `hjorth_mobility`, and `hjorth_complexity`
- compare directly against the frozen pass44 anchor on subject scores, prediction flips, margin, and headline subject metrics

The goal is narrow: see whether `brux2` can rise materially without sacrificing the pass44 `brux1` rescue or reopening controls. [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]

## Chosen measurement/reporting upgrade
Standardize a paired subject-surface audit whenever two runs share the same subjects, per-subject window counts, and evaluation contract.

Immediate next use:
- compare the future pass45 shape-ablation run directly against pass44

Minimum paired artifact contents:
- per-subject mean probability deltas
- subject prediction flips
- best-bruxism-minus-highest-control margin change
- copied-through denominator counts, exact CI block, and Brier summaries from the underlying LOSO reports

## Backup branch not promoted yet
Backup branch: add only `evt_bursts_per_episode_mean` on top of the frozen pass42/pass44 trio in one repaired cross-family add-back audit.

Why not yet: the literature support is real, but the current repo-grounded asymmetry is still more shape- and amplitude-centered than event-centered, so the smaller shape-only test should go first. ^[../projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md]

## Artifact
Primary repo report: `projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md`
