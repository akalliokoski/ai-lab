---
title: Artifact Card v2 vs v3
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md]
---

# Artifact Card v2 vs v3

Side-by-side comparison of the third `artifact-card-sft` patch against the stronger `artifact-card-v2` baseline. This page exists to preserve the negative result clearly: targeted full-card prompt scaffolding improved one field but regressed others. [[artifact-card-sft]] [[artifact-card-v1-vs-v2]] [[fine-tuning-lessons-from-first-project]] [[artifact-driven-experiment-debugging]]

## What stayed fixed
- model family: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- training entrypoint: `modal/train_unsloth_artifact_card.py`
- run length: `20` steps
- eval split: `8` held-out rows
- output schema:
  - `run_id`
  - `dataset_name`
  - `model_name`
  - `verdict`
  - `primary_failure_modes`
  - `key_evidence`
  - `next_action`

## What changed in v3
- added a short selection-hints block to every prompt
- added 6 targeted contrast rows for the exact v2 confusion patterns
- made next-action mapping more explicit inside the prompt
- kept the candidate vocabulary fixed so the metric change isolates the dataset/prompt patch rather than a schema change

## Run summary

| pass | run_id | train_rows | train_loss | valid_json_rate | exact_card_match_rate |
|---|---|---:|---:|---:|---:|
| v2 | `20260430T073913Z` | `20` | `2.108652096986771` | `1.0` | `0.0` |
| v3 | `20260430T091500Z` | `26` | `2.017786604166031` | `1.0` | `0.0` |

## Tuned field accuracy comparison

| field | v2 | v3 | change |
|---|---:|---:|---:|
| `run_id` | `1.0` | `1.0` | `0.0` |
| `dataset_name` | `1.0` | `1.0` | `0.0` |
| `model_name` | `1.0` | `1.0` | `0.0` |
| `verdict` | `0.75` | `0.625` | `-0.125` |
| `primary_failure_modes` | `0.125` | `0.125` | `0.0` |
| `key_evidence` | `0.875` | `0.625` | `-0.25` |
| `next_action` | `0.125` | `0.5` | `+0.375` |

## Main interpretation
- `artifact-card-v3` was a mixed result, not a clean improvement.
- The v3 patch materially improved exact `next_action` selection.
- But it did not move `primary_failure_modes`, and it regressed both `verdict` and `key_evidence`.
- The unchanged `exact_card_match_rate = 0.0` is the most important summary because it shows the full-card task still is not learning all fields together reliably.

## How the regression showed up in artifacts
- The tuned model sometimes copied prompt scaffolding or non-canonical wording into the output instead of sticking to the exact evidence phrases.
- One held-out `regressed` case came back as `regraded`, which is a useful reminder that lower loss did not buy better semantic normalization.
- Some rows got the action right while getting the evidence or failure modes wrong, which means the patch sharpened one boundary but destabilized the others.

## What this says about the task
- `artifact-card-sft` is still a better first-project choice than the old tutor task.
- But the full-card supervision now appears to have field interference: improving one field can make another worse.
- This is the point where another round of “just add more contrast rows” is no longer the cleanest experiment.

## Practical conclusion
- treat `artifact-card-v2` as the best current full-card baseline
- keep `artifact-card-v3` as a documented negative result about over-scaffolding the full-card prompt
- branch the next experiment into smaller supervised tasks such as:
  - `next_action` selection only
  - `primary_failure_modes` selection only
  - or a staged pipeline that predicts fields separately before recombining

## Why this comparison matters for learning
This comparison teaches a different lesson from `artifact-card-v1-vs-v2`: constraining the task helped, but adding more in-prompt guidance to the full card did not monotonically improve all fields. Once cross-field tradeoffs appear, the next disciplined move is often task decomposition rather than further prompt accretion. [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]]
