---
title: Bruxism CAP pass46 bursts-per-episode add-back review
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md
  - ../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md
  - ../raw/articles/rmma-during-sleep-humans-2001.md
  - ../raw/articles/sleep-bruxism-detection-criteria-ikeda-1996.md
  - ../raw/articles/portable-masseter-emg-validity-2019.md
  - ../raw/articles/rmma-clusters-sleep-fragmentation-pain-2024.md
  - ../raw/articles/sleep-bruxism-episode-index-misuse-2025.md
---

# Bruxism CAP pass46 bursts-per-episode add-back review

Question: after `pass45` closed the smaller same-table shape-cleanup branch but left the honest benchmark verdict `ambiguous`, is `evt_bursts_per_episode_mean` now the right single feature to add back on the frozen repaired `pass42/pass45` scaffold, and what should count as pass46 success or failure beyond the headline counts? [[bruxism-cap]] [[bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05]] [[bruxism-cap-pass45-next-step-synthesis-2026-05-05]]

## Answer in one sentence
Yes. `evt_bursts_per_episode_mean` is now the right one-feature add-back because it is the smallest feature that captures burst density within an episode, matches the strongest RMMA literature directly, and avoids reopening the cruder episode-index family first. ^[../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md]

## Why this feature, specifically
The repo's validated event trio already covers occupancy, burst duration, and inter-burst spacing. What it does not directly encode is whether the retained bursts are mostly isolated or organized into denser multi-burst packets. `evt_bursts_per_episode_mean` is exactly that missing episode-composition axis. In the current code it is just burst count divided by reconstructed episode count, so it stays compact and auditable rather than introducing a broad new family. ^[../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md]

The main source-level reason is Lavigne 2001: RMMA episodes were defined as three or more consecutive masseter-EMG bursts, and bruxers had about twice as many bursts per episode as controls with RMMA. Smardz 2024 then reinforces that cluster structure, not just generic event presence, is physiologically meaningful. ^[../raw/articles/rmma-during-sleep-humans-2001.md] ^[../raw/articles/rmma-clusters-sleep-fragmentation-pain-2024.md]

## Why not reopen raw count or episode-index features first
The strongest explicit rejection is `evt_episode_count_30s`. Newer literature directly warns against over-interpreting the episode index, and the earlier pass42 sweep already gave that family weaker repo-contact support than the kept trio. The candidate subset containing `evt_episode_count_30s` reached the same headline but with a weaker margin (`+0.324`) and a higher `n11` (`0.494`) than the kept trio (`+0.339`, `0.486`). ^[../raw/articles/sleep-bruxism-episode-index-misuse-2025.md] ^[../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md]

## What pass46 success should look like
The most important pass46 success signature is not another unchanged `1/2` and `3/3` headline. It is a targeted repaired-`A3-only` subject-surface improvement relative to frozen `pass45`:
- `brux2` rises materially from `0.178`
- `brux1` does not materially give back the `0.641` rescue
- highest control stays at or below `0.345`
- best-bruxism-minus-highest-control margin improves beyond `+0.295`

The strongest success would be `brux2` clearing the repaired `A3-only` highest control while `brux1` stays above it too. ^[../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md]

## What pass46 failure should look like
Treat the add-back as a clean failure if it mostly behaves like a raw density confound: `brux2` stays nearly flat, `brux1` regresses materially, controls rise, or the highest control reopens above the pass45 surface. If that happens, the negative result should be preserved as evidence that the repaired branch is near its compact event-organization limit rather than as a reason to reopen crude count families broadly. ^[../projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md]

## Artifact
Primary repo report: `projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md`
