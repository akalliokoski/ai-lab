---
title: Bruxism CAP pass43 matched A1-vs-A3 transfer audit
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md
  - ../projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.json
  - bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05.md
  - bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04.md
---

# Bruxism CAP pass43 matched A1-vs-A3 transfer audit

Question: if the repo keeps the verified pass42 event subset fixed (`evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`), does that small repaired `brux1` lift transfer from the repaired `EMG1-EMG2` `A1-only` scaffold onto the closest existing matched `A3-only` EMG surface? [[bruxism-cap]] [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

## Answer in one sentence
Only partially: `brux1` itself essentially holds on the old matched `A3-only` surface (`0.176 -> 0.176` versus pass14 baseline, and `0.176` versus pass42 `A1` `0.136`), but the honest subject-level transfer still collapses overall because sensitivity stays `0.000`, balanced accuracy stays `0.500`, and the repaired `A1-only` pass42 advantage does not carry over to `brux2` or the full subject ranking. [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]]

## Exact implementation path
- Reused the repaired pass42 `A1-only` anchor directly from the saved pass41 event-block table and saved pass42 LOSO report.
- Started the `A3-only` side from the existing matched14 EMG table `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`.
- Recomputed only the same 3 pass42 event features for those exact saved `A3-only` rows, merged them onto the pass14 table, and reran LOSO with the same base regex exclusions (`^bp_`, `^rel_bp_`, `^ratio_`) and no model-family change.
- Because the old pass14 table did not carry `relative_time_quantile` or `time_match_rank`, this pass derived those metadata fields per subject only for audit/readout parity; it did not rerun the underlying selector. ^[../projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md]

## Verified counts and parity checks
- Repaired pass42 `A1-only` table: `5` subjects × `10` rows each = `50` rows total.
- Existing matched14 `A3-only` baseline: `5` subjects × `14` rows each = `70` rows total.
- New pass43 `A3-only` transfer table preserved those same `70` rows exactly and added the fixed 3-feature event subset with zero merge nulls.
- Subject set stayed fixed at `brux1`, `brux2`, `n3`, `n5`, `n11` and both sides stayed on `EMG1-EMG2`.
- The main parity warning is therefore scaffold size, not subject drift: repaired `A1-only` and old matched14 `A3-only` are the same channel family but not the same row-count surface. ^[../projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md]

## Subject-level comparison
### A1 repaired fixed-subset anchor (`pass42`)
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- subject scores: `brux1 0.136`, `brux2 0.825`, `n3 0.155`, `n5 0.199`, `n11 0.486`

### A3 old matched14 baseline (`pass14`)
- balanced accuracy `0.500`
- sensitivity `0.000`
- specificity `1.000`
- subject scores: `brux1 0.176`, `brux2 0.074`, `n3 0.267`, `n5 0.266`, `n11 0.095`

### A3 fixed-subset transfer run (`pass43`)
- balanced accuracy `0.500`
- sensitivity `0.000`
- specificity `1.000`
- subject scores: `brux1 0.176`, `brux2 0.130`, `n3 0.208`, `n5 0.128`, `n11 0.310`

## What transferred and what did not
What transferred:
- `brux1` did not regress on the old `A3-only` surface; it stayed essentially flat versus pass14 and slightly above the repaired `A1` pass42 score.
- `n3` and `n5` both improved versus the old pass14 `A3-only` baseline, so the 3-feature subset is not meaningless on `A3`.

What did not transfer:
- `brux2` stayed far below the repaired `A1` pass42 anchor (`0.130` vs `0.825`).
- The highest `A3` control after transfer became `n11` at `0.310`, still well above `brux1` (`0.176`), so `brux1` remains below the top control by `0.134`.
- The best-bruxism-minus-highest-control margin stays negative on `A3` (`-0.134`) while pass42 `A1` is clearly positive (`+0.339`).

So the honest read is narrower than "the subset failed": `brux1` hold is real, but the repaired `A1-only` benchmark gain does not transfer honestly across the full matched `A3-only` surface. [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]]

## Practical interpretation
Pass43 changes the branch decision in a useful way:
- keep the pass42 3-feature subset fixed
- preserve that the subset is not purely `A1-only` noise, because it does carry some directional signal onto `A3`
- but do not claim a family-level transfer win, because the honest `A3` subject surface still collapses back to zero sensitivity
- treat the old matched14 `A3-only` scaffold itself as the next uncertainty, not the event subset definition

## Best next bounded step
Keep the exact same 3-feature event subset fixed and rebuild only the `A3-only` comparison table on the repaired percentile-band / time-aware `EMG1-EMG2` scaffold before any broader feature, model, privacy, or LLM/RL change. That is the smallest next step that can separate a true family-transfer failure from an artifact of comparing repaired `A1-only` rows against an older `A3-only matched14` surface.

## Artifacts
- Primary repo report: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md`
- Transfer report JSON: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.json`
- Transfer LOSO report: `projects/bruxism-cap/reports/loso-cv-pass43-emg-a3-matched14-eventsubset.json`
- Transfer feature table: `projects/bruxism-cap/data/window_features_pass43_emg_s2_mcap_a3_only_matched14_eventsubset.csv`
