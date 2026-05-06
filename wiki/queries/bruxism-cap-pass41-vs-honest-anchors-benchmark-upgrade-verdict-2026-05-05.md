---
title: Bruxism CAP pass41 vs honest anchors and benchmark-upgrade verdict
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md
  - ../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json
  - ../comparisons/bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05.md
  - bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05.md
  - bruxism-cap-tiny-subject-benchmarking-upgrade-2026-05-05.md
---

# Bruxism CAP pass41 vs honest anchors and benchmark-upgrade verdict

Question: after the pass41 event-conditioned audit and the tiny-subject benchmarking patch both landed, did the new branch materially improve the honest benchmark, did the new outputs improve interpretability, and what exact bounded step should come next? [[bruxism-cap]] [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]] [[bruxism-cap-tiny-subject-benchmarking-upgrade-2026-05-05]]

## Short answer

No material honest benchmark improvement yet. `pass41` is more informative than `pass37`-`pass40` because it slightly lifts `brux1` and makes the new control failure easier to localize, but on the metric that matters it regresses against both `pass36` and `pass40`, and it still does not beat the stronger matched `C4-P4` comparator context. The reporting patch does improve interpretability, but mainly by making the negative result easier to trust and communicate, not by changing the benchmark verdict itself. [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]]

## Honest-anchor verdict

### Against `pass36`
- `pass36` subject summary: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `pass41` subject summary: balanced accuracy `0.583`, sensitivity `0.500`, specificity `0.667`
- `brux1` only rises from `0.112` to `0.118`
- `n11` crosses from `0.489` to `0.546`, which is the whole reason specificity breaks

So `pass41` is not a material honest improvement over `pass36`; it trades a tiny target lift for a real control regression. ^[../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md]

### Against `pass40`
- `pass40` keeps the same honest headline as `pass36`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `pass41` still loses that comparison despite being outside the closed floor family
- the best-bruxism-minus-highest-control margin also regresses from `+0.363` in `pass40` to `+0.257` in `pass41`

So `pass41` is more diagnostically useful than another same-family floor swap, but it is not a better benchmark state than `pass40`. [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]] [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]]

### In `C4-P4` comparator context
The comparator context still matters because the strongest matched honest `C4-P4` anchor remains `pass29`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`, with `brux1=0.405` and `brux2=0.959`. `pass41` reaches the same sensitivity but only by keeping `brux2` as the lone recovered subject while introducing a false positive on `n11`; its `brux1` score (`0.118`) remains far below the matched `C4-P4` anchor's `brux1` score (`0.405`).

That means the pass41 event block does not justify changing the current comparison-anchor story: `EMG1-EMG2` remains the primary branch to improve, but the repo should still preserve `pass29 C4-P4` as the honest comparison anchor rather than presenting `pass41` as having caught up. [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]]

## Did interpretability improve?

Yes, but the improvement is in the readout, not the benchmark outcome.

The new benchmark patch makes the negative result more interpretable in three practical ways:
- it adds explicit denominator counts, so `1/2` sensitivity and `2/3` specificity are shown directly rather than only as point estimates
- it adds exact and Wilson `95%` intervals, which exposes how wide the uncertainty still is on this tiny `5`-subject scaffold
- it adds `subject_probability_brier` and `mean_positive_probability`, which make calibration-lite and per-subject score interpretation clearer than the old `mean_score`-only output

For `pass41`, that means the repo can now preserve the negative result with its uncertainty attached instead of just saying “`0.583` balanced accuracy.” The upgraded pass41 output shows:
- sensitivity counts `1/2`, exact CI `[0.013, 0.987]`
- specificity counts `2/3`, exact CI `[0.094, 0.992]`
- subject-level Brier score `0.236`

That is a real interpretability gain because it clarifies that the apparent differences between nearby passes are still very noisy on such a tiny benchmark. The important nuance is that older anchors like `pass29 C4-P4` were produced before this patch, so the improved interpretability is currently strongest on the newly generated EMG artifacts and has not yet been backfilled uniformly across every historical anchor. [[bruxism-cap-tiny-subject-benchmarking-upgrade-2026-05-05]]

## What pass41 still taught us

`pass41` should be preserved as a first-class negative-but-informative result, not discarded as random noise.

Why it still matters:
- the early catastrophic `brux1` trio softens materially relative to `pass36` and `pass40`
- the event block is net-helpful against `n5`
- the dominant unresolved gap is still the older record-relative amplitude / dispersion block, not proof that event-conditioned structure is irrelevant
- the new failure is localized more clearly to `n11`, which gives a tighter bounded follow-up than another broad feature expansion

So the benchmark verdict stays negative, but the diagnosis improved. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]] [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]]

## Exact next bounded task

Keep the same repaired five-subject scaffold, the same train-time exclusions, the same `logreg` LOSO contract, and the same 7 appended event features available in the pass41 table. Then run exactly one same-table ablation pass that keeps only the 3 least control-damaging event features, starting by dropping the event terms most implicated in the `n11` reopening.

Concretely, the next task should be:
- start from `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- keep `pass36` plus the event block scaffold fixed
- test one bounded subset rather than inventing new features
- primary goal: see whether the small `brux1` lift survives while `n11` falls back below threshold

Do not pivot to privacy work, LLM/RL work, another broad feature expansion, or a channel change from this result. Future branches remain gated because the evidence changed diagnosis, not the benchmark gate. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

## Files updated in this preservation step

Wiki files updated:
- `wiki/queries/bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/index.md`
- `wiki/log.md`

Additional repo code files updated in this preservation step:
- none
