---
title: Bruxism CAP EMG brux2 vs n3 gap audit (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.md
  - ../projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.json
  - concepts/bruxism-cap.md
---

# Question
What exactly is causing the current `EMG1-EMG2` working point to lose the honest baseline, and is the main EMG failure still diffuse or now localized to one specific subject/control reversal?

# Short answer
The current EMG-first failure is now localized more tightly than before: the decisive regression is `brux2` collapsing below `n3`, not a uniform drop across every subject.

On the strongest current EMG working point (`pass19`, matched `EMG1-EMG2 A3-only` with spectral / ratio exclusions), the `brux2 - n3` subject-score gap is `-0.193` (`0.088 - 0.280`). On the honest `C4-P4 A1-only` anchor, that same subject pair had a `+0.551` gap (`0.795 - 0.245`). So the pair flips by `-0.743`, which is the sharpest remaining benchmark failure in the repo right now.

# What the audit found

## 1. The largest surviving control-favoring EMG signal is now narrow
Inside the fixed pass19 EMG recipe, the biggest `n3`-over-`brux2` contribution delta comes from `zero_crossing_rate` (`+2.064` toward `n3`). Smaller control-favoring support comes from `burst_fraction` (`+0.414`) and `sample_entropy` (`+0.110`).

That means the current gap is not best summarized as “all EMG features fail.” It is better summarized as: a small recurring crossing / irregularity family is still enough to lift `n3` above `brux2` on the matched scaffold.

## 2. The EMG scaffold still contains some bruxism-aligned signal
The same audit also shows one clear counter-signal: `burst_rate_hz` pushes toward `brux2` (`-1.057` in the `n3 - brux2` delta table, meaning it favors `brux2` over `n3`).

So the working point is not empty. It contains both:
- a control-favoring crossing / irregularity surface
- a weaker bruxism-favoring burst-rate surface

The current honest failure is that the first one still outweighs the second.

## 3. The matched-14 scaffold is count-matched, but not time-position-matched
The pass24 audit also records a non-feature validity caveat that matters for the next extraction step:
- `brux2` kept windows have mean `start_s` `4377.9`
- `n3` kept windows have mean `start_s` `8327.1`

So the current matched comparison equalizes subject count and window count, but it does **not** equalize where in the night the retained windows come from. That does not prove causality, but it is a concrete remaining validity hole and a better next extraction check than another broad feature rewrite.

# Why this matters
This result tightens the project interpretation again:
- the current honest EMG bottleneck is now better localized than “EMG is worse than C4”
- the repo has a concrete next extraction question that stays EMG-first and leakage-aware
- the strongest durable EMG working point is still pass19, but it should now be treated as a validity scaffold for time-position and residual-artifact auditing rather than as a near-miss detector

# Recommended next bounded step
Keep the pass19 EMG recipe fixed and test one extraction-validity move before any new model change:

1. rebuild the same matched `EMG1-EMG2 A3-only` scaffold with a simple time-position matching rule across subjects, or
2. if staying purely on the audit surface, test whether `zero_crossing_rate` / `sample_entropy` are acting as residual artifact proxies for the `n3` versus `brux2` split

The safer next experiment is the first one, because it checks a concrete measurement hole without changing model family or broadening feature scope.
