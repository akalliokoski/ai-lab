# Post-pass44 verdict — does pass45 produce a real honest-benchmark improvement?

Date: 2026-05-05
Status: completed benchmark verdict memo.

## Question
Does the new post-pass44 experiment (`pass45` repaired `A3-only` no-shape) materially improve the honest benchmark once it is compared against both repaired anchors (`pass42` repaired `A1-only` and `pass44` repaired `A3-only`) rather than only against train-loss or tiny-N headline counts?

## Verdict in one line
Verdict: ambiguous.

Pass45 is a real repaired-`A3-only` score-surface improvement over pass44, but it is not yet a clean honest-benchmark improvement over the current repaired anchors because the primary subject-level headline stays unchanged and the branch still rescues only one of the two bruxism subjects.

## Anchor comparison
### Headline subject metrics
- pass42: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass44: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass45: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So the strict honest headline does not improve.

### Subject-surface comparison versus pass44
- `brux1`: `0.532 -> 0.641` (`+0.109`)
- `brux2`: `0.123 -> 0.178` (`+0.055`)
- highest control (`n11`): `0.395 -> 0.345` (`-0.049`)
- best-bruxism-minus-highest-control margin: `+0.138 -> +0.295` (`+0.158`)
- subject prediction flips: `[]`
- subject Brier: `0.256 -> 0.211`

This is a meaningful local improvement on the repaired `A3-only` surface.

### Subject-surface comparison versus pass42
- pass42 best bruxism subject remains `brux2` at `0.825`
- pass45 best bruxism subject is `brux1` at `0.641`
- pass42 highest control is `n11` at `0.486`
- pass45 highest control is `n11` at `0.345`
- pass42 best-bruxism-minus-highest-control margin: `+0.339`
- pass45 best-bruxism-minus-highest-control margin: `+0.295`

So pass45 improves the repaired `A3-only` branch internally, but it still does not beat the repaired `A1-only` anchor on the current honest separation criterion because the lost `brux2` rescue is still unrecovered.

## Control-surface read
- `brux1` is above the key control surface on pass45: `0.641 > 0.345`
- `brux2` is still below the key control surface on pass45: `0.178 < 0.345`
- therefore the branch still does not have both bruxism subjects above the highest control
- the control surface did not reopen: no control crossed the `0.5` threshold, and the highest control fell rather than rose

## Why the verdict is ambiguous instead of positive
A positive verdict would require more than a cleaner repaired-`A3-only` surface. It would need at least one of the following on the honest benchmark:
1. a better subject-level headline than `0.750 / 0.500 / 1.000`, or
2. both bruxism subjects staying above the highest control on the matched repaired surface, or
3. a repaired `A3-only` result that clearly surpasses the repaired `A1-only` anchor.

Pass45 does none of those yet. But calling it negative would also overstate the case, because the paired same-table audit shows a real improvement versus pass44 with no control reopening and no contract drift.

## Exact next bounded step
Keep pass45 as the repaired `A3-only` anchor and run exactly one backup add-back on the frozen repaired scaffold: add only `evt_bursts_per_episode_mean` on top of the fixed pass42/pass45 trio while keeping the subject set, selector, channel family, threshold, and `logreg` LOSO contract unchanged.

## Bottom line
Pass45 is real progress on the repaired `A3-only` branch, not noise and not train-loss theater. But it is still only a partial benchmark rescue, so the honest benchmark verdict should remain `ambiguous` until `brux2` also clears the key control surface or the headline subject metrics move.