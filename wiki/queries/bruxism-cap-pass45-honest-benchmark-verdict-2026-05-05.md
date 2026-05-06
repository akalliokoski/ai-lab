---
title: Bruxism CAP pass45 honest benchmark verdict
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md
  - ../projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md
  - ../projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.md
  - bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05.md
---

# Bruxism CAP pass45 honest benchmark verdict

Question: does the post-pass44 experiment (`pass45` repaired `A3-only` no-shape) produce a real honest-benchmark improvement once it is judged against both repaired anchors rather than only by tiny-N headline counts? [[bruxism-cap]] [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]] [[bruxism-cap-pass42-pass44-cross-family-methodology-review-2026-05-05]]

## Answer in one sentence
Verdict: ambiguous. `pass45` is a real repaired-`A3-only` surface improvement over `pass44`, but it is not yet a clean honest-benchmark improvement because the subject-level headline stays fixed at `0.750 / 0.500 / 1.000` and only `brux1`, not both bruxism subjects, clears the highest control. ^[../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md]

## Comparison against the repaired anchors
Headline subject metrics are unchanged across all three repaired runs:
- `pass42`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `pass44`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `pass45`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000` ^[../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md]

But the repaired `A3-only` surface does improve locally versus `pass44`:
- `brux1`: `0.532 -> 0.641`
- `brux2`: `0.123 -> 0.178`
- highest control (`n11`): `0.395 -> 0.345`
- best-bruxism-minus-highest-control margin: `+0.138 -> +0.295`
- subject Brier: `0.256 -> 0.211`
- no subject prediction flips versus `pass44` ^[../projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md]

Compared with `pass42`, the unresolved benchmark limit is still the missing `brux2` rescue: repaired `A1-only` keeps `brux2` at `0.825`, while repaired `A3-only` no-shape only reaches `0.178`; correspondingly, `pass45` still trails `pass42` on best-bruxism-minus-highest-control margin (`+0.295` versus `+0.339`). ^[../projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.md] ^[../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md]

## Control-surface read
- `brux1` is above the key control surface on `pass45` (`0.641 > 0.345`)
- `brux2` is still below the key control surface on `pass45` (`0.178 < 0.345`)
- the branch therefore still does not put both bruxism subjects above the highest control
- the control surface did not reopen: no control crossed the `0.5` threshold, and the highest control decreased relative to `pass44` ^[../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md]

## Why the verdict stays ambiguous
Calling the result positive would overclaim from tiny-N stability because the honest subject-level headline does not improve and the repaired `A3-only` branch still fails to recover both bruxism subjects above the control surface. Calling it negative would also be too strong, because the same-table paired audit shows a real local gain versus `pass44` with no control reopening or contract drift. The most faithful label is therefore `ambiguous`: real branch progress, but not yet a benchmark-level win. [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]]

## Exact next bounded step
Keep `pass45` as the repaired `A3-only` anchor and run exactly one backup add-back on the frozen repaired scaffold: add only `evt_bursts_per_episode_mean` on top of the fixed pass42/pass45 trio while keeping the subject set, selector, channel family, threshold, and `logreg` LOSO contract unchanged. [[bruxism-cap-pass45-next-step-synthesis-2026-05-05]]
