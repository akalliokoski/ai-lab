---
title: Artifact Card Failure Modes V1 vs Binary V1
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, failure-analysis]
sources: [concepts/artifact-card-sft.md, ../docs/first-artifact-card-experiment.md]
---

# Artifact Card Failure Modes V1 vs Binary V1

This comparison documents the next supervision redesign after the first `primary_failure_modes`-only branch failed to improve. The key question was: if the model judges one candidate label at a time instead of emitting the full 2-label set directly, does the task become more learnable? [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]]

## What changed

### `artifact-card-failure-modes-v1`
- Output: one JSON object with `primary_failure_modes`
- Supervision shape: emit the final 2-label list directly
- Train/eval rows: 26 / 8
- Run: `20260430T094854Z`

### `artifact-card-failure-modes-binary-v1`
- Output: one JSON object with `candidate_label` and `belongs`
- Supervision shape: judge one candidate failure label at a time
- Train/eval rows: 208 / 64
- Run: `20260430T104259Z`

## Metric comparison

### Direct branch metrics
- `artifact-card-failure-modes-v1`
  - valid JSON: `1.0`
  - exact-match accuracy on `primary_failure_modes`: `0.125`
- `artifact-card-failure-modes-binary-v1`
  - base valid JSON: `0.984375`
  - tuned valid JSON: `1.0`
  - base exact binary row match: `0.359375`
  - tuned exact binary row match: `0.71875`
  - tuned `candidate_label` accuracy: `0.984375`
  - tuned `belongs` accuracy: `0.734375`

## What improved
- The binary framing was much easier for the model to format and parse.
- It strongly improved per-row supervision compared with the base model.
- The model almost always copied the candidate label correctly and answered with valid JSON.

## What still failed
- Reconstructing the final 2-label answer from the 64 one-label judgments still failed on every held-out case.
- Reconstructed exact top-2 set match across the 8 original eval examples was `0.0`.
- The tuned model predicted `no-material-change` as positive on 7 of 8 eval cases.
- It predicted `missing-required-detail` as negative on all 8 eval cases, even though that label was truly positive on 6 of the 8 cases.

## Interpretation
- This is a mixed but useful result.
- The supervision redesign clearly helped the model learn the local binary judgment format.
- But the learned decision boundary is still too biased to recover the final label set correctly.
- So the next bottleneck is no longer “can the model emit the right output shape?” and not simply “can it judge one label at a time?”
- The remaining problem is how to force a better calibrated final selection rule for the positive labels.

## Best current conclusion
- Simple decomposition (`artifact-card-failure-modes-v1`) was too weak.
- Binary candidate judgment (`artifact-card-failure-modes-binary-v1`) is a better supervision direction because it produces a strong row-level signal.
- But it should not yet be treated as a solved subtask because the reconstructed top-2 failure-mode prediction is still unusable.
- The next cleaner branch should likely enforce a stronger decision structure, such as:
  - choose exactly two positive labels
  - compare labels pairwise under a fixed rubric
  - or score each label against explicit evidence snippets before ranking the final set
