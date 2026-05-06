---
title: Bruxism CAP pass42 event-subset ablation verdict
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, experiment, evaluation, notes]
sources:
  - ../projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv
  - ../projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json
  - bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05.md
  - bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05.md
---

# Bruxism CAP pass42 event-subset ablation verdict

Question: if the pass41 same-table event-conditioned block is reduced to the least control-damaging 3-feature subset, can the repo preserve the small `brux1` lift without reopening `n11`, and does that count as a real benchmark upgrade? [[bruxism-cap]] [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]] [[bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05]]

## Short answer

Yes on the narrow preservation goal, no on the benchmark-upgrade goal. The best pass42 3-feature subset restores the pass36 honest headline (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity) while keeping the small event-driven `brux1` improvement and pushing `n11` back below threshold, but `brux1` still has `0/10` positive windows and remains far from a threshold-relevant recovery. So pass42 is the least control-damaging event-subset version of pass41, not a real benchmark breakthrough.

## What stayed fixed

- same repaired five-subject `SLEEP-S2 + MCAP-A1-only` scaffold
- same `EMG1-EMG2` channel
- same pass36 base table with the pass41 event-conditioned append available
- same train-time exclusions for `^bp_`, `^rel_bp_`, and `^ratio_`
- same `logreg` LOSO subject-level evaluation contract
- only bounded change: enumerate all `35` three-feature subsets of the `7` pass41 event features and keep the least control-damaging survivor

## Winning pass42 subset

Best no-reopen subset:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Headline subject-level result:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- `brux1`: `0.1365` (`+0.0249` vs pass36 `0.1116`)
- `brux2`: `0.8246`
- `n3`: `0.1553`
- `n5`: `0.1994`
- `n11`: `0.4861` (back below the `0.5` threshold)
- best-bruxism-minus-highest-control margin: `+0.3386`

Window-level subject counts at the fixed threshold:
- `brux1`: `0/10` positive windows
- `brux2`: `10/10`
- `n3`: `1/10`
- `n5`: `0/10`
- `n11`: `3/10`

This is exactly the bounded preservation target from the pass41 review: keep a small `brux1` lift while closing the reopened `n11` control failure. It succeeds on that narrow contract. ^[../projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json]

## Why this is still not a true upgrade

Pass42 improves the pass41 failure mode more than it improves the benchmark frontier.

Relative to pass41 with all 7 event features:
- pass41: balanced accuracy `0.583`, specificity `0.667`, `brux1=0.118`, `n11=0.546`
- pass42 best subset: balanced accuracy `0.750`, specificity `1.000`, `brux1=0.136`, `n11=0.486`

So the subset ablation clearly fixes the reopened-control problem and keeps more of the `brux1` gain than pass36 alone. But the meaningful limitation survives: `brux1` is still predicted as `control` with zero positive windows, while `brux2` remains the only clearly recovered bruxism subject. That means the event subset is same-table safe, but not sufficient to change the repo's honest handoff story. [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]]

## Comparison to nearby bounded alternatives

The no-reopen top three all preserved the same honest headline, but the winning subset above had the largest `brux1` lift:

1. `evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`
   - `brux1=0.1365`, `n11=0.4861`, lift `+0.0249`
2. `evt_bursts_per_episode_mean`, `evt_active_fraction`, `evt_phasic_like_episode_fraction`
   - `brux1=0.1343`, `n11=0.4557`, lift `+0.0228`
3. `evt_burst_count_30s`, `evt_active_fraction`, `evt_phasic_like_episode_fraction`
   - `brux1=0.1295`, `n11=0.4562`, lift `+0.0179`

A nearby higher-`brux1` candidate that kept `evt_active_fraction` and `evt_burst_duration_median_s` but swapped in `evt_phasic_like_episode_fraction` instead of `evt_interburst_gap_median_s` did not survive the control contract: `brux1` rose further to `0.1544`, but `n11` reopened to `0.5399` and the honest subject-level verdict fell back to `0.583` balanced accuracy with `0.667` specificity.

That makes the pass42 verdict sharper than “event features help” or “event features fail.” The useful signal is that event activity + duration can help, but the third term has to be chosen conservatively to avoid reactivating `n11`, and even the safest subset still does not recover `brux1` at threshold.

## Uncertainty-aware interpretation

The uncertainty-aware reporting surface still matters here even though the headline stayed flat. The preserved sweep output for the winning no-reopen subset kept the same tiny-subject denominator pattern as pass36 on the honest endpoint: sensitivity `1/2`, specificity `3/3`, with a subject-level Brier score of about `0.215`. The practical interpretation is unchanged from the pass41 instrumentation update: the subset result is more trustworthy as a narrow negative-or-mixed preservation step than as a large performance claim, because tiny changes in subject ordering on this `5`-subject scaffold still sit inside very wide uncertainty bands. [[bruxism-cap-tiny-subject-benchmarking-upgrade-2026-05-05]]

## Exact preserved verdict

Pass42 should be preserved as: the best same-table event-subset ablation closes the pass41 `n11` reopening and modestly improves `brux1` over pass36, so it is the least control-damaging event-conditioned variant so far; however, it still leaves `brux1` below threshold with `0/10` positive windows and therefore does not justify any benchmark-victory framing, branch activation, or model-family pivot.

## Exact next bounded step

Do not broaden from this result. Keep the same repaired scaffold and the same event-subset framing, but treat pass42 as a selection result rather than an endpoint. The best next bounded benchmark increment is one compact follow-up that keeps the pass42 subset fixed and changes only one representation detail inside that subset, such as a light subject-relative rescaling or a threshold/rule calibration memo for the retained event terms, before any privacy, LLM/RL, channel, or broad feature-family branch activation. [[bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05]] [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

## Files updated in this preservation step

Wiki files updated:
- `wiki/queries/bruxism-cap-pass42-event-subset-ablation-verdict-2026-05-05.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/index.md`
- `wiki/log.md`

Additional repo code files updated in this preservation step:
- none
