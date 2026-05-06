# Bruxism CAP campaign handoff

Date: 2026-05-05
Status: revised after the full post-pass44 repaired `A3-only` branch closed through the negative `pass46` add-back verdict and the fresh post-pass46 next-step synthesis.

## Campaign verdict

Continue the current autoresearch loop.

But continue it narrowly and honestly: the branch learned something real, but it still did not produce a clean benchmark win and still does not justify reopening the broader campaign frame.

The durable verdict is now:
- keep the repo on the current CAP, EMG-first, leakage-aware benchmark framing
- keep `pass29 C4-P4` as the honest comparison-channel anchor
- keep `pass45` as the durable repaired `A3-only` anchor
- preserve `pass46` only as a biologically coherent side-variant negative-result memo, not as a promoted replacement
- preserve that the overall honest campaign read still stays `ambiguous`: the repaired branch improved locally, but the headline still stays `0.750 / 0.500 / 1.000` and the unresolved `brux2` miss remains
- queue exactly one new bounded repaired-`A3-only` experiment before reopening privacy, LLM/RL, channel, scaffold, dataset, or broader feature-search questions

## What moved in the pass45/pass46 branch

### 1. `pass45` remains the clean repaired `A3-only` anchor
`pass45` is still the strongest repaired `A3-only` reference because it keeps the honest headline fixed while materially improving the paired subject surface versus `pass44`:
- `brux1`: `0.532 -> 0.641`
- `brux2`: `0.123 -> 0.178`
- highest control: `0.395 -> 0.345`
- best-bruxism-minus-highest-control margin: `+0.138 -> +0.295`
- subject Brier: `0.256 -> 0.211`

That remains real local benchmark progress, not only train-loss noise or artifact churn.

### 2. `pass46` moved `brux2`, but not enough to replace `pass45`
`pass46` restored only `evt_bursts_per_episode_mean` on top of the frozen `pass45` repaired `A3-only` no-shape scaffold.

What moved:
- `brux2`: `0.178 -> 0.196`
- `brux2 - highest_control`: `-0.167 -> -0.151`
- controls stayed below threshold

What did not move enough:
- `brux1` stayed essentially flat: `0.641 -> 0.639`
- the headline stayed fixed at `0.750 / 0.500 / 1.000`
- the paired repaired-`A3-only` best-bruxism-minus-highest-control margin slipped slightly: `+0.295 -> +0.292`

So `pass46` is worth preserving as a meaningful negative result, but not as the new repaired `A3-only` anchor.

### 3. The branch bottleneck is now narrower again
The live question is no longer whether one extra event-organization feature can move `brux2` at all. `pass46` answered that yes, directionally.

The unresolved bottleneck is narrower:
- repaired `A3-only` is still count-matched but subject-unstable
- `brux1` stays rescued on the repaired no-shape `A3-only` surface
- `brux2` still remains below the highest control
- one extra density-style feature was not selective enough to fix that miss

So the next move should stay inside the compact event-organization lane, but leave the exact failed one-feature density add-back lane.

## Future-branch gate status

Gate status: unchanged and still closed.

Do not promote either future branch yet:
- privacy/PET next task remains `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`
- the first LLM/RL tasks remain wiki-first bounded memos or prototypes

Why the gates stay closed:
- subject-level sensitivity is still only `0.500`
- the headline subject verdict did not improve
- `brux2` still fails to clear the highest control on repaired `A3-only`
- the benchmark still has one smaller repaired-surface experiment available before broader expansion is justified

## Should the autoresearch loop continue or pause?

Continue.

Reason:
- the branch still produced real repaired-`A3-only` learning
- the negative result is now sharper rather than noisier
- the surviving next question is narrower than another broad feature or branch expansion

Do not pause for reframing yet.

## Single best next bounded task

Run exactly one frozen-`pass45` repaired-`A3-only` event-trio swap:
- keep the repaired `pass45` table, subject set, selected rows, threshold, channel family, `logreg` LOSO contract, base exclusions, and shape-drop exclusions fixed
- keep `evt_active_fraction`
- keep `evt_burst_duration_median_s`
- drop only `evt_interburst_gap_median_s`
- add only `evt_phasic_like_episode_fraction`
- compare directly against the unchanged `pass45` anchor with the paired subject-surface audit, not against headline counts alone

This is now the best next task because it stays outside the failed `evt_bursts_per_episode_mean` add-back lane, keeps the event block width fixed at three features, preserves the safer backbone terms, and tests the strongest surviving distinct episode-organization hypothesis for the unresolved `brux2` miss.

## What should not be queued next

Do not queue any of these before that fixed-width trio swap:
- promoting `pass46` over `pass45`
- another immediate one-feature density/count add-back such as `evt_burst_count_30s`
- `evt_episode_count_30s`
- reopening the full seven-feature event block
- another scaffold rewrite
- a model-family pivot
- a channel switch or fusion branch
- a dataset switch away from CAP
- a privacy/PET implementation task
- an LLM/RL prototype task

## Bottom line

The post-pass44 repaired `A3-only` branch produced two durable outcomes:
- `pass45` is the clean repaired `A3-only` anchor
- `pass46` is a first-class negative side variant that keeps the event-organization idea alive but closes the exact one-feature density add-back lane

The repo now knows that:
- the repaired `A3-only` branch did improve honestly at the paired subject-surface level
- the honest campaign-level read still stays `ambiguous`, not benchmark-positive
- privacy and LLM/RL gates did not move
- the exact next bounded step is one frozen-`pass45` event-trio swap: replace only `evt_interburst_gap_median_s` with `evt_phasic_like_episode_fraction`
