---
title: Bruxism CAP pass46 next-step synthesis
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass46-next-step-synthesis-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md
  - ../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md
  - bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05.md
  - bruxism-cap-pass46-one-feature-addback-2026-05-05.md
---

# Bruxism CAP pass46 next-step synthesis

Question: after `pass46` closed the exact one-feature `evt_bursts_per_episode_mean` add-back lane as a negative repaired-`A3-only` side variant, what is the single best next bounded experiment that still survives repo contact? [[bruxism-cap]] [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]] [[bruxism-cap-pass46-one-feature-addback-2026-05-05]]

## Answer in one sentence
Run one frozen-`pass45` repaired-`A3-only` event-trio swap: keep `evt_active_fraction` and `evt_burst_duration_median_s`, drop only `evt_interburst_gap_median_s`, add only `evt_phasic_like_episode_fraction`, and judge it with the paired subject-surface audit rather than headline counts alone.

## Why this is the live bottleneck
`pass46` already answered the narrow question of whether one extra event-organization feature can move `brux2` at all. It can, but not enough:
- `brux2`: `0.178 -> 0.196`
- highest control: `0.345 -> 0.347`
- repaired `A3-only` best-bruxism-minus-highest-control margin: `+0.295 -> +0.292`
- headline stays `0.750 / 0.500 / 1.000` ^[../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md]

So the unresolved miss is still broad under-support for `brux2` on repaired `A3-only`, not total absence of event signal. [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]]

## What survives repo contact
The compact event-organization lane still survives:
- repaired `pass42` and repaired `pass44` validated the base event trio cross-family
- `pass45` remains the repaired `A3-only` anchor
- `pass46` showed that one extra organization term can move `brux2` directionally without reopening thresholded controls

But the exact `evt_bursts_per_episode_mean` add-back lane does not survive as the next promoted move. [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]] [[bruxism-cap-pass46-one-feature-addback-2026-05-05]]

## Exactly one chosen experiment
Chosen experiment: run one frozen-`pass45` repaired-`A3-only` event-trio swap that drops only `evt_interburst_gap_median_s` and adds only `evt_phasic_like_episode_fraction`.

Exact definition:
1. Reuse the frozen `pass45` repaired `A3-only` no-shape table and LOSO contract.
2. Keep subject set, selected rows, threshold, channel, model family, base exclusions, and shape-drop exclusions fixed.
3. Keep `evt_active_fraction` fixed.
4. Keep `evt_burst_duration_median_s` fixed.
5. Remove only `evt_interburst_gap_median_s`.
6. Add only `evt_phasic_like_episode_fraction`.
7. Compare directly against unchanged `pass45` with a paired subject-surface audit. ^[../projects/bruxism-cap/reports/pass46-next-step-synthesis-2026-05-05.md]

## Why this one wins
This is the best surviving move because:
- it is outside the exact failed `evt_bursts_per_episode_mean` density add-back lane
- it keeps the event block width fixed at three features rather than broadening to four or seven
- it directly tests whether the weakest retained trio member on repaired `A3-only` is `evt_interburst_gap_median_s`
- it preserves the safer backbone features that repeatedly survived repo contact: `evt_active_fraction` and `evt_burst_duration_median_s`
- it uses the strongest remaining distinct episode-organization idea without collapsing back into crude count/density proxies

## Success and failure read
Success should look like:
- `brux2` rises materially above the `pass45` value (`0.178`)
- `brux1` stays near the `pass45` rescue
- no control crosses threshold
- the paired repaired-`A3-only` best-bruxism-minus-highest-control margin improves beyond `+0.295`

Failure should look like:
- `brux2` stays nearly flat or only cosmetically better while the highest control rises
- `brux1` materially regresses
- the paired repaired-`A3-only` margin stays flat or worsens again

## Carry-forward reporting rule
Every new matched run should include a paired subject-surface audit against the frozen anchor with copied-through exact CI blocks and subject-level Brier summaries. `pass45` and `pass46` proved that headline counts alone are not enough to distinguish a real repaired-surface gain from a negative side variant. [[bruxism-cap-pass46-honest-benchmark-verdict-2026-05-05]]

## Artifacts
- Repo synthesis memo: `projects/bruxism-cap/reports/pass46-next-step-synthesis-2026-05-05.md`
- Benchmark verdict: `projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md`
- Supporting result note: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md`
