---
title: Artifact Card Failure Modes Binary V1 vs Top2 V1
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, failure-analysis]
sources: [concepts/artifact-card-sft.md, ../docs/first-artifact-card-experiment.md]
---

# Artifact Card Failure Modes Binary V1 vs Top2 V1

This comparison documents the next attempt after the binary branch. The question was: if the model is forced to output the final exactly-two-label decision directly, with ranked keys `first_label` and `second_label`, does that work better than one-label-at-a-time binary judgment? [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]]

## What changed

### `artifact-card-failure-modes-binary-v1`
- Output: `candidate_label`, `belongs`
- Supervision shape: one label at a time
- Train/eval rows: 208 / 64
- Run: `20260430T104259Z`

### `artifact-card-failure-modes-top2-v1`
- Output: `first_label`, `second_label`
- Supervision shape: one final exactly-two-label ranked decision
- Train/eval rows: 26 / 8
- Run: `20260430T122543Z`

## Metric comparison

### `artifact-card-failure-modes-binary-v1`
- tuned valid JSON: `1.0`
- tuned exact binary row match: `0.71875`
- tuned `candidate_label` accuracy: `0.984375`
- tuned `belongs` accuracy: `0.734375`
- reconstructed final top-2 label-set exact match: `0.0`

### `artifact-card-failure-modes-top2-v1`
- tuned valid JSON: `1.0`
- tuned exact final-pair match: `0.0`
- tuned `first_label` accuracy: `0.125`
- tuned `second_label` accuracy: `0.0`

## What regressed
- The stronger final-decision prompt did not recover the top-2 task.
- It performed worse than the binary branch on every local metric that matters.
- It also failed the downstream exact-pair objective, keeping `0.0` exact match.

## How the failure showed up in artifacts
- The tuned model collapsed to `missing-required-detail` as `first_label` on 7 of 8 eval rows.
- It rotated among `hallucinated-detail`, `phrase-copy-or-template-collapse`, and `wrong-causal-point` as a weak second guess.
- It missed both `no-material-change` eval cases and both `fluency-without-correctness` eval cases.
- The overlap-related eval row was also missed, predicting `wrong-causal-point` + `missing-required-detail` instead of `overlap-contaminated-eval` + `phrase-copy-or-template-collapse`.

## Interpretation
- This is a clean negative result.
- Forcing the final top-2 decision directly did not improve calibration.
- It pushed the model back toward a repeated default pair pattern instead of learning a sharper final ranking rule.
- Lower train loss (`1.9992237269878388`) did not translate into better held-out label selection.

## Best current conclusion
- `artifact-card-failure-modes-binary-v1` remains the strongest supervision redesign so far because it at least learned the local label-judgment task.
- `artifact-card-failure-modes-top2-v1` is a useful negative result showing that a harder final-decision prompt alone is not enough.
- The next promising branch should likely add a true comparison structure, such as pairwise label ranking or evidence-conditioned per-label scoring, instead of asking the model to jump straight to the final ranked pair.
