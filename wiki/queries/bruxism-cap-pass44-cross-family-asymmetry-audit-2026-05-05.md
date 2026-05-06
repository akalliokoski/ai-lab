---
title: Bruxism CAP pass44 cross-family asymmetry audit
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md
  - ../projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md
  - ../projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md
  - bruxism-cap-pass44-repaired-a3-event-subset-rebuild-2026-05-05.md
  - bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05.md
---

# Bruxism CAP pass44 cross-family asymmetry audit

Question: after pass44 repaired the `A3-only` scaffold and recovered the same honest headline as the repaired pass42 `A1-only` anchor, what asymmetry is actually left on the fixed 3-feature event subset, and what is the safest next bounded test? [[bruxism-cap]] [[bruxism-cap-pass44-repaired-a3-event-subset-rebuild-2026-05-05]] [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]]

## Answer in one sentence
The remaining bottleneck is not cross-family transfer anymore but a within-family subject split on repaired `A3-only`: pass44 rescues `brux1` to `0.532` while leaving `brux2` collapsed at `0.123`, and the evidence says the split is carried primarily by the retained amplitude / dispersion block rather than by the small retained event block.

## Exact asymmetry after pass44
Subject-level scores on the repaired surfaces:
- pass42 repaired `A1-only`: `brux1 0.136`, `brux2 0.825`, `n3 0.155`, `n5 0.199`, `n11 0.486`
- pass44 repaired `A3-only`: `brux1 0.532`, `brux2 0.123`, `n3 0.034`, `n5 0.365`, `n11 0.395`

So pass44 keeps the same headline subject-level result (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity), but it does so by swapping which bruxism subject is recovered rather than by lifting both. ^[../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md]

## Why `brux1` is rescued while `brux2` collapses
The repaired `A3-only` amplitude / dispersion surface is the dominant difference:
- `brux1` block means: amp/disp `+14.070`, shape `-1.404`, event `+0.058`, other `+1.219`
- `brux2` block means: amp/disp `-0.048`, shape `-0.735`, event `+0.117`, other `+0.060`
- `brux1 - brux2` block delta: amp/disp `+14.118`, shape `-0.670`, event `-0.059`, other `+1.159`

Time-rank summaries make the mechanism more specific:
- `brux1` has an early-rank `1-3` pocket with mean score `1.000` and amp/disp mean `+40.076`
- `brux1` then decays through the mid and late ranks (`0.412`, then `0.225`)
- `brux2` stays uniformly low across early, mid, and late rank groups (`0.124`, `0.132`, `0.108`)

So the repaired A3 selector exposes a concentrated early amplitude / dispersion pocket for `brux1`, but not for `brux2`. The remaining failure is therefore not one catastrophic `brux2` window group like the old early-`brux1` problem; it is a broad lack of positive support for `brux2` across the whole repaired A3 table. ^[../projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md]

## Which retained families look most responsible
### Primary driver: amplitude / dispersion
This is the main asymmetry carrier.
- `brux1` amp/disp changes from pass42 `-49.074` to pass44 `+14.070` (`+63.144`)
- `brux2` amp/disp changes only from `-0.713` to `-0.048` (`+0.665`)
- `n3` becomes much safer because its amp/disp block falls from `+0.189` to `-9.104`

Inside that block, the single largest contribution-gap term between `brux1` and `brux2` is `mean`:
- `mean` contribution `brux1 +16.163` vs `brux2 -0.052` (delta `+16.215`)

### Secondary driver: compact shape block
Shape is not the main rescue signal, but it probably contributes to `brux2` staying low.
- `brux2` shape mean falls from pass42 `+2.313` to pass44 `-0.735`
- `brux1` shape mean also falls, but less decisively relative to its newly positive amp/disp surface

### Not the main blocker: retained 3-feature event block
The fixed event subset still matters diagnostically, but it is too small to explain the post-pass44 subject split by itself:
- `brux1 - brux2` event-block delta is only `-0.059`
- the biggest pass44 block separation still lives in amp/disp, not event features

## Practical interpretation
Pass44 closes the old transfer question and opens a narrower one:
- do not call the retained subset `A1`-locked anymore
- do not reopen the pass43 scaffold-mismatch verdict
- read the remaining gap as a repaired-`A3` subject-allocation problem inside the retained representation
- keep the next step same-table and family-local rather than broadening the branch

## Best next bounded step
Keep the exact repaired pass44 `A3-only` table fixed and run one same-table shape-only ablation:
- keep selected rows, train-time exclusions, and the retained 3 event features fixed
- drop only the compact shape family (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`)
- compare subject scores against the unchanged pass44 anchor

Why this is the safest next move: it tests the second-strongest plausible cause of the `brux1`/`brux2` split without touching the repaired selector, channel, event subset, or model family. [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]

## Explicitly rejected broader move
Rejected move: another scaffold rewrite or model-family pivot.

Why rejected: pass44 already answered the scaffold-transfer question, and the current asymmetry is now localized enough that another selector rewrite, broad feature search, or model swap would blur the diagnosis instead of testing it.

## Artifact
Primary repo report: `projects/bruxism-cap/reports/pass44-cross-family-asymmetry-audit.md`
