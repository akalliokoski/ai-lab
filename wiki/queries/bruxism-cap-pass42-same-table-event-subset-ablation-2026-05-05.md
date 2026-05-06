---
title: Bruxism CAP pass42 same-table event-subset ablation
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md
  - ../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.json
  - bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05.md
  - bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05.md
---

# Bruxism CAP pass42 same-table event-subset ablation

Question: if the repo keeps the repaired five-subject `EMG1-EMG2`, `A1-only`, `pass36` backbone fixed and reuses the already-generated pass41 table, can one bounded 3-feature event subset preserve the small `brux1` lift while pushing `n11` back below threshold? [[bruxism-cap]] [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]] [[bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05]]

## Answer in one sentence
Yes, directionally: keeping only `evt_active_fraction`, `evt_burst_duration_median_s`, and `evt_interburst_gap_median_s` restores the honest subject-level surface to `0.750` balanced accuracy and `1.000` specificity, moves `n11` back below threshold (`0.546 -> 0.486`), and lifts `brux1` further (`0.118 -> 0.136`), though `brux1` still remains below threshold and still trails `n3`. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Exact subset and selection path
The chosen pass42 subset is:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Selection path:
- reuse the exact pass41 feature table rather than regenerating features
- score all `35` choose-3 subsets of the existing seven `evt_*` columns on the same LOSO subject-level surface
- rank subsets by: keep `n11 < 0.5`, then maximize `brux1` uplift, then maximize best-bruxism-minus-highest-control margin, then balanced accuracy

Under that bounded rule, this subset is the strongest same-table follow-up because it keeps the pass41 directional target gain while repairing the reopened control. ^[../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md]

## What improved versus pass41
Compared with the full pass41 event block:
- balanced accuracy recovers from `0.583` to `0.750`
- specificity recovers from `0.667` to `1.000`
- `n11` falls from `0.546` to `0.486`, so the pass41 false-positive subject closes again
- `brux1` rises further from `0.118` to `0.136`
- the best-bruxism-minus-highest-control margin improves from `+0.257` to `+0.339`

So the same-table ablation does what the pass41 follow-up was supposed to test: the event idea was not dead, but the full seven-feature raw bundle was too wide for this tiny scaffold. [[bruxism-cap-pass41-event-conditioned-feature-block-audit-2026-05-05]]

## What did not improve enough
The benchmark is still not solved:
- subject-level sensitivity stays `0.500`
- `brux1` is still below the `0.5` subject threshold
- `brux1` still trails `n3` (`0.136` vs `0.155`)
- `n5` and `n11` are both still above `brux1`, even though `n11` is now back under threshold

So pass42 is a better local state than pass41 and a cleaner diagnostic state than another floor-family tweak, but it is still a partial rescue rather than a handoff-grade benchmark win. [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Practical interpretation
Pass42 changes the branch decision in a useful but still narrow way:
- keep the event-subset idea alive
- treat the winning subset as verified on the current repaired scaffold
- do not broaden again immediately to another 7-feature expansion, deep model, privacy branch, or LLM/RL branch
- use the verified subset as the new bounded comparison surface for the next question

The strongest next bounded question is now channel/scaffold transfer, not another same-table subset search. [[bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05]]

## Best next bounded step
Keep the exact pass42 subset fixed and compare that same subset on matched `EMG1-EMG2` `A1-only` versus matched `EMG1-EMG2` `A3-only` tables before changing model family. That asks whether the new subset win is specific to the repaired `A1-only` scaffold or transfers cleanly across the closest existing EMG comparison surface. [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]]

## Artifact
Primary repo report: `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md`
