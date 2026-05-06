---
title: Bruxism CAP pass46 honest benchmark verdict
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md
  - ../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md
  - bruxism-cap-pass46-bursts-per-episode-add-back-review-2026-05-05.md
  - bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05.md
---

# Bruxism CAP pass46 honest benchmark verdict

Question: does `pass46`, which restores only `evt_bursts_per_episode_mean` on the frozen repaired `pass42/pass45` scaffold, materially improve the honest benchmark enough to replace `pass45` as the repaired `A3-only` anchor? [[bruxism-cap]] [[bruxism-cap-pass46-one-feature-addback-2026-05-05]] [[bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05]]

## Answer in one sentence
No: `pass46` is biologically well-motivated and gives a believable but tiny `brux2` lift, yet it leaves the headline fixed, keeps `brux2` below the highest control, slightly worsens the paired repaired-`A3-only` margin versus `pass45`, and therefore does not count as a real honest-benchmark improvement.

## Required comparison against the anchors
Headline subject metrics remain identical across all three repaired anchors:
- pass42: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass45: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass46: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity ^[../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md]

The repaired `A3-only` surface moves only slightly from pass45 to pass46:
- `brux1`: `0.641 -> 0.639`
- `brux2`: `0.178 -> 0.196`
- highest control: `0.345 -> 0.347`
- best-bruxism-minus-highest-control margin: `+0.295 -> +0.292` ^[../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md]

Against repaired `pass42`, pass46 still loses on the unresolved cross-family criterion:
- pass42 best-bruxism-minus-highest-control margin: `+0.339`
- pass46 best-bruxism-minus-highest-control margin: `+0.292`
- pass42 `brux2 - highest_control`: `+0.339`
- pass46 `brux2 - highest_control`: `-0.151` ^[../projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md]

## Are `brux1` and `brux2` above or below the highest control?
- `brux1` is above the highest control on pass46: `0.639 > 0.347`
- `brux2` is below the highest control on pass46: `0.196 < 0.347`

So the repaired `A3-only` branch still rescues only one of the two bruxism subjects.

## Did the control surface reopen?
No.

No control crosses `0.5`, and the run keeps the repaired control surface formally closed. But it also does not tighten the surface overall, because the highest control rises slightly from `0.345` to `0.347` and the paired best-bruxism margin slips slightly.^[../projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md]

## Does the feature-specific literature support the observed movement?
Yes, directionally.

The literature review for this branch argues that `evt_bursts_per_episode_mean` is the right one-feature restore because RMMA science distinguishes denser multi-burst episode composition from crude episode counts. Lavigne 2001 is the most direct source-level support, Smardz 2024 reinforces cluster structure as physiologically meaningful, Ikeda 1996 and Yamaguchi 2020 support event-thresholded subject-relative jaw-EMG summaries, and Wieckiewicz 2025 is the main reason not to reopen `evt_episode_count_30s` first. That makes the small selective `brux2` lift believable, but it still falls short of the review's own success bar because `brux2` remains below the highest control and the paired repaired-`A3-only` margin does not improve.^[../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md]

## Verdict
Verdict: negative.

This is not a "noise only" result, but it is still negative on the actual benchmark question. The add-back is scientifically interpretable and mildly encouraging for the specific feature hypothesis, yet it does not produce a material honest-benchmark gain over either repaired anchor. [[bruxism-cap-pass46-bursts-per-episode-add-back-review-2026-05-05]] [[bruxism-cap-pass46-one-feature-addback-2026-05-05]]

## Exact next bounded step
Keep `pass45` as the durable repaired `A3-only` anchor, preserve `pass46` as a side-variant negative-result memo, and spend the next benchmark card on one new bounded experiment outside this exact one-feature add-back lane rather than stacking more interpretation onto the same tiny shift.

## Artifacts
- Repo report: `projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md`
- Supporting result note: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md`
- Paired audit: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md`
- Literature review: `projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md`
