---
title: Bruxism CAP pass44 repaired A3-only event-subset rebuild
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md
  - ../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.json
  - bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05.md
  - bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05.md
---

# Bruxism CAP pass44 repaired A3-only event-subset rebuild

Question: if the repo keeps the verified pass42 3-feature event subset fixed and rebuilds only the `EMG1-EMG2` `A3-only` comparison table on the repaired percentile-band / time-aware scaffold, does the pass43 transfer failure remain, or was the old matched14 `A3-only` scaffold the main blocker? [[bruxism-cap]] [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]] [[bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05]]

## Answer in one sentence
The old scaffold was the main blocker: once `A3-only` is rebuilt on the repaired `cap=10`, `lower_quantile=0.10`, `upper_quantile=0.90` time-aware surface and the same 3 event features are merged back in, the honest subject-level result returns to the pass42 anchor at `0.750` balanced accuracy, `0.500` sensitivity, and `1.000` specificity instead of the pass43 collapse to `0.500` / `0.000` / `1.000`.

## Exact implementation path
- Rebuilt the `EMG1-EMG2` `A3-only` feature pool on the repaired shape scaffold rather than reusing the old matched14 `A3-only` surface.
- Applied the repaired percentile-band selector with `cap=10`, `lower_quantile=0.10`, and `upper_quantile=0.90` to recover a time-aware `10`-windows-per-subject comparison table.
- Kept the pass42 event subset fixed at `evt_active_fraction`, `evt_burst_duration_median_s`, and `evt_interburst_gap_median_s`, merged by `subject_id`, `start_s`, `end_s`, and `window_index`, and verified zero merge nulls.
- Reran the unchanged LOSO evaluation path (`train_baseline.py --cv loso`) with the same base exclusions `^bp_`, `^rel_bp_`, and `^ratio_`, while excluding the other four pass41 event columns so the scaffold changes, not the training rule set, explain the result. ^[../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md]

## Verified scaffold parity
- pass42 repaired `A1-only` anchor: `50` rows total = `10` rows per subject across `brux1`, `brux2`, `n11`, `n3`, `n5`
- pass43 old matched14 `A3-only` transfer table: `70` rows total = `14` rows per subject
- pass44 rebuilt full `A3-only` pool: `298` rows total with per-subject counts `{'brux1': 31, 'brux2': 111, 'n11': 42, 'n3': 76, 'n5': 38}`
- pass44 repaired selected/final `A3-only` table: `50` rows total = `10` rows per subject, exactly matching the repaired pass42 scaffold size
- Event merge null counts after the repaired rebuild: `0` for all three retained event features ^[../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md]

## Subject-level comparison
### pass42 repaired `A1-only` anchor
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`

### pass43 old matched14 `A3-only` transfer run
- balanced accuracy `0.500`
- sensitivity `0.000`
- specificity `1.000`

### pass44 repaired `A3-only` rebuild
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`

The repaired `A3-only` rebuild therefore recovers the same honest subject-level headline as pass42 and removes the main negative interpretation from pass43: the fixed 3-feature event subset was not the limiting factor once the timing surface is rebuilt fairly.

## Practical interpretation
- The verified pass42 event subset is stronger than the pass43 mixed verdict implied when evaluated on a fair `A3-only` scaffold.
- The dominant confound in the pass42-vs-pass43 comparison was scaffold mismatch (`50` repaired rows versus `70` older matched14 rows), not a family-specific failure of the retained event features.
- This is still not a benchmark handoff-grade win, because the repaired surface only returns to the existing pass42 ceiling rather than beating it: `brux1` is rescued, but `brux2` still does not clear threshold and subject-level sensitivity remains `0.500`.

## Best next bounded step
Preserve pass44 as the repaired cross-family baseline and continue only with similarly bounded changes that try to improve the collapsed `brux2` verdict without sacrificing the new `brux1` rescue, rather than re-litigating whether the 3 retained event features transfer beyond `A1-only`. Privacy and LLM/RL branches should remain gated until a later benchmark step converts this repaired-scaffold recovery into a real threshold-relevant gain.

## Artifacts
- Primary repo report: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md`
- Summary JSON: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json`
- Rebuilt full pool: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_full_envelope_shape.csv`
- Repaired selector report: `projects/bruxism-cap/reports/time-position-match-pass44-emg-a3-pct10-90-shape.json`
- Intermediate selected table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_shape.csv`
- Final feature table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
