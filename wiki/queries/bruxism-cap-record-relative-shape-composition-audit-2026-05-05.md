---
title: Bruxism CAP record-relative plus shape composition audit
date: 2026-05-05
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit-summary.json
  - ../projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md
  - ../projects/bruxism-cap/reports/pass35-shape-feature-expansion.md
---

# Bruxism CAP record-relative plus shape composition audit

Question: do the two best current EMG representation clues on the repaired five-subject `A1-only` percentile-band scaffold actually compose honestly when stacked on the exact same selected rows? [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]

## Answer
Yes, but only partially.

The strict pass34-versus-pass36 comparison keeps the repaired scaffold fixed and adds only the four pass35 shape features on top of the pass34 record-relative table. Under that apples-to-apples comparison, subject-level balanced accuracy rises from `0.500` to `0.750`, sensitivity rises from `0.000` to `0.500`, specificity stays `1.000`, and the best-bruxism-minus-highest-control margin improves from `+0.041` to `+0.319`. [[bruxism-cap]]

The gain is carried by `brux2`, not by a full benchmark rescue: `brux2` rises from `0.480` to `0.808` and becomes the only held-out positive subject, while `n3` drops sharply from `0.439` to `0.068`. But `brux1` regresses from `0.180` to `0.112`, so the benchmark is still bottlenecked by one bruxism subject rather than by generic control inversion.

## What this changes
- `pass34` and `pass35` should no longer be treated only as separate mixed-result clues; the composition does produce a real honest subject-level gain on the repaired EMG scaffold.
- The next bounded question should stay on the same scaffold and localize the remaining `brux1` failure, rather than pivoting immediately to another channel or broad branch.
- Negative-result discipline still matters here: this is not a full EMG win because only one of the two bruxism subjects crosses threshold. [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]] [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]]

## Key numbers
- pass34 subject metrics: balanced_accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- pass36 subject metrics: balanced_accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass34 `n3 - brux1`: `+0.259`
- pass36 `n3 - brux1`: `-0.043`
- pass34 `brux2 - n3`: `+0.041`
- pass36 `brux2 - n3`: `+0.740`
- pass34 best-bruxism-minus-highest-control: `+0.041`
- pass36 best-bruxism-minus-highest-control: `+0.319`
