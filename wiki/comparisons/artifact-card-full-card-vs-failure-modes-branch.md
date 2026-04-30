---
title: Artifact Card Full Card vs Failure-Modes Branch
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md]
---

# Artifact Card Full Card vs Failure-Modes Branch

Side-by-side comparison of the strongest full-card baseline against the first decomposed `primary_failure_modes`-only branch. This page exists to preserve a second negative result clearly: simple output decomposition did not improve the weakest semantic field. [[artifact-card-sft]] [[artifact-card-v2-vs-v3]] [[fine-tuning-lessons-from-first-project]] [[artifact-driven-experiment-debugging]]

## What is being compared
- Full-card baseline: `artifact-card-v2`
- Full-card patched run: `artifact-card-v3`
- Decomposed branch: `artifact-card-failure-modes-v1`

All three used:
- model family: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- training entrypoint: `modal/train_unsloth_artifact_card.py`
- run length: `20` steps
- eval split size: `8` held-out rows

## What changed in the decomposed branch
- removed `verdict`, `key_evidence`, and `next_action` from the target output
- kept the same underlying run evidence as `artifact-card-v3`
- reduced the output to one JSON key: `primary_failure_modes`
- added dataset-level `task_config.json` so the shared training/eval pipeline could score only the narrowed field

## Run summary

| pass | run_id | train_rows | train_loss | valid_json_rate | tracked metric |
|---|---|---:|---:|---:|---:|
| full-card v2 | `20260430T073913Z` | `20` | `2.108652096986771` | `1.0` | `primary_failure_modes = 0.125` |
| full-card v3 | `20260430T091500Z` | `26` | `2.017786604166031` | `1.0` | `primary_failure_modes = 0.125` |
| failure-modes-v1 | `20260430T094854Z` | `26` | `2.363450402021408` | `1.0` | `exact primary_failure_modes match = 0.125` |

## Main result
- The decomposed branch did not improve the held-out `primary_failure_modes` score.
- It matched the same `0.125` level reached by the full-card runs.
- It also did not beat the base model on the same eval split.

## How the failure showed up in artifacts
- The tuned failure-modes-only model repeatedly predicted `missing-required-detail` plus `phrase-copy-or-template-collapse`.
- That collapse happened on 5 of 8 held-out rows.
- The branch did recover the overlap-specific eval row exactly, but it still failed to distinguish nearby pairs involving:
  - `no-material-change`
  - `generic-explanation`
  - `hallucinated-detail`
  - `fluency-without-correctness`
- This means the problem did not disappear when the other card fields were removed.

## What this comparison rules out
- It weakens the simple hypothesis that cross-field interference was the only reason `primary_failure_modes` stayed weak.
- It suggests the deeper bottleneck is in the label semantics or in how the evidence is framed for this field.

## Practical conclusion
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-v1` as a documented negative result, not as an improvement claim
- the next disciplined branch should likely redesign the supervision for this field more aggressively, for example:
  - pairwise label-choice prompts
  - one-label-at-a-time evidence judgments
  - or a two-stage predictor that scores each candidate label before selecting the final top 2

## Why this comparison matters for learning
This comparison sharpens the decomposition lesson. Splitting a weak field out of a larger task is a good diagnostic move, but it is not automatically enough. If the narrowed branch still fails, that points to a more specific problem in label design or evidence presentation, which is a much more useful next diagnosis than simply saying the full-card task was hard. [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]]
