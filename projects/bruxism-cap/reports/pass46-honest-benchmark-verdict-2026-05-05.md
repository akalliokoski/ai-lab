# Post-pass45/pass46 verdict — does pass46 materially improve the honest benchmark?

Date: 2026-05-05
Status: completed benchmark verdict memo.

## Question
Does the one-feature `pass46` add-back (`evt_bursts_per_episode_mean` on the frozen repaired `pass42/pass45` scaffold) materially improve the honest benchmark once it is judged against both repaired anchors (`pass42` repaired `A1-only` and `pass45` repaired `A3-only`) rather than headline counts, train loss, or unpaired anecdotes?

## Verdict in one line
Verdict: negative.

`pass46` is biologically coherent and directionally interesting, but it does not produce a real honest-benchmark improvement. The subject-level headline is unchanged, `brux2` remains below the highest control, the repaired `A3-only` paired margin slips slightly versus `pass45`, and repaired `pass42` still remains the strongest control-separated anchor.

## Anchor comparison
### Headline subject metrics
- pass42: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass45: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass46: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So the strict honest headline does not improve at all.

### Subject-surface comparison versus pass45
- `brux1`: `0.641 -> 0.639` (`-0.002`)
- `brux2`: `0.178 -> 0.196` (`+0.018`)
- highest control: `0.345 -> 0.347` (`+0.002`, `n11 -> n5`)
- best-bruxism-minus-highest-control margin: `+0.295 -> +0.292` (`-0.004`)
- subject prediction flips: `[]`
- subject Brier: `0.211 -> 0.207`

This is too small and too mixed to count as a material repaired-`A3-only` improvement over the pass45 anchor.

### Subject-surface comparison versus pass42
- pass42 best bruxism subject remains `brux2` at `0.825`
- pass46 best bruxism subject is `brux1` at `0.639`
- pass42 highest control is `n11` at `0.486`
- pass46 highest control is `n5` at `0.347`
- pass42 best-bruxism-minus-highest-control margin: `+0.339`
- pass46 best-bruxism-minus-highest-control margin: `+0.292`
- `brux2 - highest_control`: pass42 `+0.339` vs pass46 `-0.151`

So `pass46` still does not recover the unresolved cross-family miss that matters most: repaired `A3-only` remains far behind repaired `A1-only` on `brux2` separation.

## Control-surface read
- `brux1` is above the highest control on pass46: `0.639 > 0.347`
- `brux2` is below the highest control on pass46: `0.196 < 0.347`
- therefore both bruxism subjects are still not above the highest control
- the control surface did not reopen: no control crossed the `0.5` threshold
- however, the surface also did not tighten overall, because the highest control moved slightly upward and the paired best-bruxism margin worsened

## Does the literature support the direction of movement?
Yes, but only as weak directional support, not as evidence of a benchmark win.

The pass46 review correctly predicted that `evt_bursts_per_episode_mean` was the right single-feature add-back to test because RMMA literature distinguishes denser multi-burst episodes from crude episode counts:
- Lavigne 2001 directly supports bursts-per-episode as a differentiating RMMA organization measure
- Ikeda 1996 and Yamaguchi 2020 support event-thresholded, subject-relative jaw-EMG summaries
- Smardz 2024 keeps cluster structure central rather than treating episodes as interchangeable counts
- Wieckiewicz 2025 warns against over-reading crude episode-index summaries, which is why `evt_episode_count_30s` was rightly not reopened first

That literature fit explains why `brux2` moving slightly upward is believable rather than random-looking. But the observed effect is still below the review's own success bar: `brux2` does not clear the highest control, `brux1` is only preserved not improved, and the paired repaired-`A3-only` margin does not beat `pass45`.

## Why the verdict is negative instead of ambiguous
`Pass45` earned an ambiguous verdict because it materially improved the repaired `A3-only` surface while leaving the honest benchmark unresolved.

`Pass46` does not clear even that bar:
1. it does not improve the headline subject metrics
2. it does not improve the paired repaired-`A3-only` margin
3. it does not put both bruxism subjects above the highest control
4. it does not beat the repaired `pass42` anchor on the best available control-separation criterion

The small `brux2` lift is scientifically informative, but on this benchmark it behaves more like weak supporting evidence for the feature choice than like a genuine benchmark upgrade.

## Exact next bounded step
Keep `pass45` as the durable repaired `A3-only` anchor and preserve `pass46` only as a side-variant negative-result memo; do not promote the add-back, and move the benchmark branch to one new bounded experiment outside this exact one-feature add-back lane rather than stacking more interpretation on the same tiny shift.

## Bottom line
`Pass46` should be recorded as a negative honest-benchmark result with a useful scientific footnote: the feature-specific literature does support trying `evt_bursts_per_episode_mean`, and the run shows a believable but too-small targeted `brux2` lift without reopening controls. That is not enough to claim a real benchmark improvement, so repaired `pass45` remains the durable `A3-only` anchor and repaired `pass42` remains the stronger control-separated comparator.