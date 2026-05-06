---
title: Bruxism CAP pass41 event-conditioned feature block audit
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, experiment, evaluation, notes]
sources:
  - ../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md
  - ../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json
  - ../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-literature-memo-2026-05-05.md
---

# Bruxism CAP pass41 event-conditioned feature block audit

Question: does appending one compact event-conditioned jaw-EMG block to the unchanged pass36 table improve the repaired five-subject CAP benchmark without reopening the controls? [[bruxism-cap]] [[bruxism-cap-pass41-event-conditioned-feature-block-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Answer in one sentence
Only directionally: the 7-feature event block lifts `brux1` slightly (`0.112 -> 0.118`) and softens the catastrophic early trio, but it reopens control risk by pushing `n11` above threshold and lowering specificity from `1.000` to `0.667`, so it is informative evidence rather than a clean benchmark win. [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]]

## What stayed fixed
- same repaired `SLEEP-S2 + MCAP-A1-only` five-subject scaffold
- same `EMG1-EMG2` channel
- same pass34 record-relative transform and pass35 compact shape merge
- same selected rows, train-time exclusions, and `logreg` LOSO contract
- only new information: 7 appended raw event-conditioned features

## Exact pass41 event block
The appended features were:
- `evt_burst_count_30s`
- `evt_episode_count_30s`
- `evt_bursts_per_episode_mean`
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`
- `evt_phasic_like_episode_fraction`

Implemented event rule:
- active sample threshold `max(2.0 * median_rectified, median_rectified + 2.0 * MAD_rectified, 1e-6)` using full-record rectified reference values
- burst duration `>=0.25 s`
- merge gaps `<0.08 s`
- group bursts into episodes when inter-burst gap `<3.0 s`
- phasic-like episode = `>=3` bursts with each burst duration in `[0.25, 2.0] s`

## Key result
Compared with both pass36 and pass40:
- `brux1` rises only slightly: `0.112 -> 0.118`
- early `brux1` ranks `1-3` mean score improves from `2.14e-82` to `1.76e-65`, so the event block is not useless
- balanced accuracy regresses from `0.750` to `0.583`
- specificity regresses from `1.000` to `0.667`
- `n11` becomes the new control failure (`0.489 -> 0.546`)
- best-bruxism-minus-highest-control margin regresses from `+0.319` / `+0.363` to `+0.257`

So the raw event block helps the target subject a bit but broadens the control-side error surface too much to count as an honest improvement. ^[../projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md]

## What the event block seems to be doing
The strongest practical read is not “event structure is wrong,” but “raw event structure is too blunt in this tiny scaffold.”

Evidence:
- for `n5 - brux1`, the net event-block contribution is actually negative, meaning several event features help `brux1` relative to `n5`
- the largest event-side negative contributor there is `evt_burst_duration_median_s`, with `evt_active_fraction` also favoring `brux1`
- but `n11` still stays above `brux1`, and the event block is slightly positive for `n11 - brux1`, so the raw appended block is not selectively rescuing the right failure surface
- the old record-relative amplitude / dispersion block still dominates the total gap against `brux1`; the event block is a perturbation, not the main decision surface yet

This points to scale and feature-selection issues inside the new event block more than to a total dead end for event-conditioned EMG. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Best next bounded step
Do not abandon the event idea, but do not broaden it either.

Best next step:
- keep the same 7-event block fixed
- run one bounded ablation on the same pass41 table, testing only the least control-damaging subset rather than all 7 event features at once
- likely start with the count / spacing terms that did not obviously blow up the controls, instead of keeping `evt_burst_duration_median_s` and `evt_active_fraction` bundled by default

A reasonable alternate bounded follow-up would be to keep the same block but make only the count / density features record-relative, because the current result looks like an event-scale mismatch more than a proof that event structure is irrelevant. [[bruxism-cap-pass41-event-conditioned-feature-block-2026-05-05]]

## Artifact
Primary repo report: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md`
