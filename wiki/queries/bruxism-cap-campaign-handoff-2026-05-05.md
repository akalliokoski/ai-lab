---
title: Bruxism CAP campaign handoff (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-next-step-synthesis-2026-05-05.md
  - bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05.md
  - bruxism-cap-pass46-next-step-synthesis-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
After the repaired `A3-only` post-pass44 branch closed through the negative `pass46` add-back verdict, should the current `bruxism-cap` autoresearch loop continue, and what exact bounded step should replace the failed one-feature density add-back lane? [[bruxism-cap]] [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]] [[bruxism-cap-pass46-next-step-synthesis-2026-05-05]]

# Short answer
Continue, but continue more narrowly.

The durable campaign-level read is now: keep `pass45` as the repaired `A3-only` anchor, preserve `pass46` only as a biologically coherent side-variant negative-result memo, keep privacy and LLM/RL gates closed, and move next to one fixed-width repaired-`A3-only` event-trio swap rather than another one-feature density/count add-back. [[bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05]] [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]]

# What moved in the branch

## 1. `pass45` still owns the repaired `A3-only` anchor
`pass45` remains the clean repaired `A3-only` reference because it materially improved the paired subject surface over `pass44` while keeping the tiny-N headline fixed:
- `brux1`: `0.532 -> 0.641`
- `brux2`: `0.123 -> 0.178`
- highest control: `0.395 -> 0.345`
- best-bruxism-minus-highest-control margin: `+0.138 -> +0.295`
- subject Brier: `0.256 -> 0.211` ^[../projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md]

## 2. `pass46` changed `brux2` directionally, but not decisively
Restoring only `evt_bursts_per_episode_mean` on top of frozen `pass45` nudged the unresolved subject in the right direction:
- `brux2`: `0.178 -> 0.196`
- `brux2 - highest_control`: `-0.167 -> -0.151`
- controls stayed below threshold

But the run still did not beat the anchor where it mattered:
- `brux1`: `0.641 -> 0.639`
- headline stayed `0.750 / 0.500 / 1.000`
- best-bruxism-minus-highest-control margin slipped `+0.295 -> +0.292` ^[../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md]

So `pass46` should be preserved as a meaningful negative result, not promoted as the new repaired `A3-only` anchor. [[bruxism-cap-pass46-one-feature-addback-2026-05-05]] [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]]

## 3. The bottleneck is now narrower than the old handoff
The current branch is no longer asking whether one extra event-organization feature can move `brux2` at all. `pass46` already showed that it can, at least slightly.

The narrower remaining bottleneck is this:
- repaired `A3-only` is still count-matched but subject-unstable
- `brux1` stays rescued on the repaired no-shape surface
- `brux2` still remains below the highest control
- one extra density-style feature was not selective enough to solve that miss

That means the next move should stay inside the compact event-organization lane, but outside the exact failed `evt_bursts_per_episode_mean` add-back lane. [[bruxism-cap-pass46-next-step-synthesis-2026-05-05]]

# Why the loop should continue

## 1. The branch still has one smaller honest question left
The surviving next question is now a fixed-width trio replacement, not a broad feature search: keep the repaired `pass45` scaffold frozen, preserve the safer event backbone terms, and test whether `evt_phasic_like_episode_fraction` is a better repaired-`A3-only` organization descriptor than `evt_interburst_gap_median_s`. [[bruxism-cap-pass46-next-step-synthesis-2026-05-05]]

## 2. Negative results became sharper, not less useful
`pass46` did not kill the event lane; it killed one exact add-back lane. That is useful because it narrows the next experiment without pretending the whole event-organization idea failed. [[bruxism-cap-pass46-bursts-per-episode-add-back-review-2026-05-05]] [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]]

## 3. Future branches remain real but still gated
The privacy/PET and LLM/RL roadmap notes remain legitimate downstream branches, but this branch did not move their activation gate. Subject-level sensitivity is still only `0.500`, the headline subject verdict did not improve, and repaired `A3-only` still fails to recover both bruxism subjects above the highest control. [[bruxism-cap-privacy-pets-roadmap-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

# Continue or pause?
Continue.

But continue on this revised durable read:
- honest comparison anchor: `pass29 C4-P4`
- repaired `A1-only` anchor: `pass42`
- repaired `A3-only` anchor: `pass45`
- pass46 label: biologically coherent side-variant negative result
- campaign-level benchmark label: still `ambiguous`, not benchmark-positive

Do not pause for reframing yet.

# Best next bounded task
Queue exactly one implementation/run task on the current board:
- reuse the frozen `pass45` repaired `A3-only` no-shape table and LOSO contract
- keep `evt_active_fraction`
- keep `evt_burst_duration_median_s`
- drop only `evt_interburst_gap_median_s`
- add only `evt_phasic_like_episode_fraction`
- keep subject set, selected rows, threshold, channel family, base exclusions, and shape-drop exclusions fixed
- require a paired subject-surface audit against frozen `pass45`

This is the highest-value next task because it stays outside the failed density/count add-back lane, keeps the event block width fixed at three features, and tests the strongest surviving repaired-`A3-only` episode-organization hypothesis without reopening scaffold, model, privacy, or LLM/RL scope. [[bruxism-cap-pass46-next-step-synthesis-2026-05-05]]
