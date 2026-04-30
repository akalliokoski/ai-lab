---
title: Artifact Card Failure Modes Top2 V1 vs Pairwise V1
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment]
sources: [concepts/artifact-card-sft.md, ../docs/first-artifact-card-experiment.md]
---

# Artifact Card Failure Modes Top2 V1 vs Pairwise V1

This comparison documents the next attempt after the direct top-2 branch. The question was: if the model is trained to compare two candidate labels at a time instead of emitting the final ranked pair directly, does that improve the real held-out `primary_failure_modes` decision? [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]]

## What changed

### `artifact-card-failure-modes-top2-v1`
- Output: `first_label`, `second_label`
- Supervision shape: one final exactly-two-label ranked decision
- Train/eval rows: 26 / 8
- Run: `20260430T122543Z`

### `artifact-card-failure-modes-pairwise-v1`
- Output: `preferred_label`
- Supervision shape: one pairwise comparison between two candidate labels
- Train/eval rows: 728 / 224
- Run: `20260430T125005Z`
- Reconstruction rule: aggregate pairwise wins back into one top-2 prediction per original eval example

## Metric comparison

### `artifact-card-failure-modes-top2-v1`
- tuned valid JSON: `1.0`
- tuned exact final-pair match: `0.0`
- tuned `first_label` accuracy: `0.125`
- tuned `second_label` accuracy: `0.0`

### `artifact-card-failure-modes-pairwise-v1`
- tuned valid JSON: `1.0`
- tuned exact pairwise row match: `0.5580357142857143`
- tuned `preferred_label` accuracy: `0.5580357142857143`
- reconstructed final top-2 exact order match: `0.0`
- reconstructed final top-2 exact set match: `0.25`

## What improved
- Pairwise supervision produced the first non-zero reconstructed held-out top-2 set match beyond the direct decomposition branch.
- The tuned pairwise run recovered 2 of the 8 original held-out label sets at the set level.
- It also preserved strict JSON validity at `1.0`.

## What still failed
- Ordered final-pair accuracy stayed at `0.0` after reconstruction.
- Pairwise row accuracy itself was only `0.5580357142857143`, so the local comparison task is still far from solved.
- The tuned reconstruction still over-promoted `missing-required-detail`, which dominated the win counts on most eval examples.

## How the failure showed up in artifacts
- For both held-out `no-material-change` + `missing-required-detail` rows, the reconstructed top-2 set was right but the ranking was reversed.
- On most other eval rows, the tuned branch still pushed `missing-required-detail` to the top and then filled the second slot with `no-material-change` or another repeated fallback.
- The overlap-related row still failed badly: the reconstructed pair became `missing-required-detail` + `no-material-change` instead of `overlap-contaminated-eval` + `phrase-copy-or-template-collapse`.

## Interpretation
- This is a mixed result, not a clean success.
- The pairwise framing did help more than direct top-2 prompting on the real downstream objective, because it raised reconstructed exact set match from `0.0` to `0.25`.
- But it still did not solve the actual ranking problem, and it did not beat the stronger local metrics of the earlier binary branch.
- The main remaining weakness is that `missing-required-detail` still behaves like a dominant default label instead of a calibrated comparison outcome.

## Best current conclusion
- `artifact-card-failure-modes-pairwise-v1` is the first comparison-style branch that improved downstream held-out set recovery at all.
- But it is still only a partial step because reconstructed ordered top-2 accuracy remains `0.0`.
- The next promising branch should likely move to evidence-conditioned per-label scoring, or a smaller contrastive subset focused on the most confused labels, rather than another generic pairwise expansion over the full 8-label space.
